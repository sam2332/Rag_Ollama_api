// ==UserScript==
// @name         Support Central AI Ticket System
// @namespace    http://tampermonkey.net/
// @version      2024-05-09
// @description  Try to take over the world!
// @author       You
// @match        https://*/SupportCentral/HelpdeskTickets/Details/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    const model = 'dolphin-mistral:latest';
    const now = new Date();
    const date = now.toLocaleDateString();
    const hours = now.getHours();
    const formattedDateTime = `${date} ${hours}:00`;

    const review_systemMessage = `
Todays Date/Time: ${formattedDateTime}
        Summarize the ticket in the following format:
 { "tasks": ["item_title1", "item_title2","many more"], "frustration_reasons": ["reason_title1", "reason_title2","many more"], "ticket_complete": Boolean,"reasons_incomplete": ["reason1","reason2","many more"]}
    Vaild Json Only, dont say the default format elements
    `;

    async function LLM(prompt, systemMessage, temperature, max_tokens, model) {
        $('#loading_id').remove();
        $('#ai_output').append("<center id='loading_id'>Loading AI Output...</center>");
        try {
            const response = await fetch('http://localhost:11435/api/passthrough/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: model,
                    cache: '1h',
                    keep_alive: '0m',
                    messages: [
                        { role: 'system', content: systemMessage },
                        { role: 'user', content: prompt }
                    ],
                    temperature: temperature,
                    max_tokens: max_tokens,
                    return_json: true
                })
            });
            const data = await response.json();
            console.log('Success:', data);
            $('#loading_id').remove();
            return data;
        } catch (error) {
            console.error('Error:', error);
            $('#loading_id').remove();
            $('#ai_output').append("Error with llm: " + error+"<br>")
            $('#ai_output').css("background-color","rgb(251 204 204)")
            // reraise the error
        }
    }
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
    
            // Create a deep clone of the element
            const clone = content[i].cloneNode(true);
    
            // Remove all links within the cloned element
            const links = clone.getElementsByTagName('a');
            while (links.length > 0) {
                links[0].parentNode.removeChild(links[0]);
            }
    
            output += compactText(clone.textContent) + "\n\n\n";
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
        return content.replace(/\n{3,}/g, '\n\n')
                      .replace(/[ \t]+(\n)/g, '$1')
                      .replace(/(\n)[ \t]+/g, '$1')
                      .replace(/[ \t]{2,}/g, ' ')
                      .trim();
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
            const gathered_ticket_comments =gatherAndCompactContentByClassName('comment')
            const ticket_id = document.location.href.split('/')[6].split('?')[0];

            await resetEmbeddingsDb(ticket_id);
            const embeddingCollection = [];
            embeddingCollection.push(generateEmbeddingItem(ticket_id, "ticket_body", gathered_ticket_information));
            
            gatherComments().forEach((comment, index) => {
                embeddingCollection.push(generateEmbeddingItem(ticket_id, "comment "+ index.toString(), comment));
            });


            const ticket_info = document.getElementsByClassName('ticket-info')[0].textContent;
            embeddingCollection.push(generateEmbeddingItem(ticket_id, "ticket_info", ticket_info));
            await batchInsert(embeddingCollection);

            const data = await LLM(gathered_ticket_information+"\n"+gathered_ticket_comments, review_systemMessage, 0.97, 24000, model);
            if (!data || !data.message || !data.message.content) {
                $('#ai_output').html("AI Offline")
                console.log(data)
                $('#ai_output').css("background-color","rgb(251 204 204)")
                return;
            }
            let output = "";
            try {
                const decoded = JSON.parse(data.message.content);
                output += "<b>Tasks:</b> <br><ul style='list-style-type: none;'>";
                for (const task of decoded.tasks) {
                    output += `<li>${task}</li>`;
                }
                output += "</ul><b>Frustration Reasons:</b> <br><ul style='list-style-type: none;'>";
                for (const reason of decoded.frustration_reasons) {
                    output += `<li>${reason}</li>`;
                }
                output += "</ul>";

                if (decoded.ticket_complete) {
                    output += "<b>Ticket Complete</b>";
                }else{
                    output += "<b>Reasons Incomplete:</b> <br><ul style='list-style-type: none;'>";
                    for (const reason of decoded.reasons_incomplete) {
                        output += `<li>${reason}</li>`;
                    }
                    output += "</ul>";
                }
            } catch (jsonError) {
                console.error('Error parsing JSON:', jsonError);
                output = data.message.content;
            }

            $('#ai_output').append(output);
        } catch (error) {
            console.error('Error during chat initiation:', error);
            $('#ai_output').append("Error Inializing: " + error + "<br>")
            $('#ai_output').css("background-color","rgb(251 204 204)")
        }
    }

    $('.comment-description').append(`
        <div style="text-align:center; width: 100%; background-color: bisque; padding: 25px;" id="ai_output">
            <center id="loading_id">Loading AI Output...</center>
        </div>
    `);

    initiateSystem();
})();
