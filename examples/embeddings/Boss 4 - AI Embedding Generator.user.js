// ==UserScript==
// @name         Boss 4 - AI Embedding Generator
// @namespace    http://tampermonkey.net/
// @version      2024-05-09
// @description  Try to take over the world!
// @author       You
// @match        https://itsm.ingham.org/SupportCentral/HelpdeskTickets/Details/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    const now = new Date();
    const date = now.toLocaleDateString();
    const formattedDateTime = `${date}`;

    function generateEmbeddingItem(ticketId, section, content) {
        return {
            source: section,
            content: content,
            overlap: 50,
            chunk_size: 1024,
            check_existing: true,
            embeddings_db: "TicketEmbeddings_" + ticketId
        };
    }

    async function batchInsert(collection) {
        const url = "http://localhost:11435/api/embeddings/batch_insert_text_embeddings";
        const headers = {
            "Content-Type": "application/json"
        };

        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: JSON.stringify({ embeddings: collection })
        });

        return response;
    }

    function gatherAndCompactContentByClassName(selector) {
        const content = document.getElementsByClassName(selector);
        let output = "";

        for (let i = 0; i < content.length; i++) {
            if (content[i].classList.contains("comment-input")) {
                continue;
            }



            output += compactText(content[i].textContent) + "\n\n\n";
        }

        return output;
    }
    function gatherComments(){
        const comments = document.getElementsByClassName('comment');
        let output = [];
        for (let i = 0; i < comments.length; i++) {
            if (comments[i].classList.contains("comment-input")) {
                continue;
            }
            output.push(compactText(comments[i].textContent))
        }
        return output;
    }

    function compactText(content) {
        return content
            .split('\n')                           // Split content into lines
            .map(line => line.trim())              // Trim each line
            .join('\n')                            // Join lines back with a single newline
            .replace(/\n{3,}/g, '\n\n')            // Replace three or more newlines with two newlines
            .replace(/[ \t]+(\n)/g, '$1')          // Remove spaces or tabs before a newline
            .replace(/(\n)[ \t]+/g, '$1')          // Remove spaces or tabs after a newline
            .replace(/[ \t]{2,}/g, ' ')            // Replace multiple spaces or tabs with a single space
            .trim();                               // Remove leading and trailing whitespace from the entire text
    }

    function tailText(text, length) {
        return text.slice(-length);
    }
    async function resetEmbeddingsDb(ticketId) {
        const url = "http://localhost:11435/api/embeddings/reset_embeddings_db";
        const headers = {
            "Content-Type": "application/json"
        };

        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                embeddings_db: "TicketEmbeddings_" + ticketId
            })
        });

        return response;
    }

    // Call the function with a ticket ID of 1
    async function initiateSystem() {
        try {
            const gathered_ticket_information = gatherAndCompactContentByClassName('comment-description')
            const gathered_ticket_comments =tailText(gatherAndCompactContentByClassName('comment'),2048)
            const ticket_id = document.location.href.split('/')[6].split('?')[0];

            await resetEmbeddingsDb(ticket_id);
            const embeddingCollection = [];
            embeddingCollection.push(generateEmbeddingItem(ticket_id, "ticket_body", compactText(gathered_ticket_information)));

            gatherComments().forEach((comment, index) => {
                embeddingCollection.push(generateEmbeddingItem(ticket_id, "comment "+ index.toString(), compactText(comment)));
            });


            embeddingCollection.push(generateEmbeddingItem(ticket_id, "ticket_info", compactText(document.getElementsByClassName('ticket-info')[0].textContent)));
            batchInsert(embeddingCollection);
        } catch (error) {
            console.error('Error during chat initiation:', error);
        }
    }


    initiateSystem();
})();
