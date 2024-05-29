// ==UserScript==
// @name         SupportCentral_TicketReview
// @namespace    http://tampermonkey.net/
// @version      2024-05-09
// @description  Try to take over the world!
// @author       You
// @match        https://*/SupportCentral/HelpdeskTickets/Details/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=ingham.org
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const model = 'dolphin-mistral:latest';
    const review_systemMessage = `
        Rate the technician and provide as many tasks as you can, and a complete list of frustrating items in the following format:
        {
            "tasks": ["item_title1", "item_title2"...],
            "frustration_reasons": ["reason_title1", "reason_title2"...]
            "ticket_complete": Boolean,
            "reasons_incomplete": ["reason1","reason2"...]
        }
        Make sure to only output the JSON object and nothing else.
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
                    max_tokens: max_tokens
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

    async function initiateChatWithSystemMessage() {
        try {
            const gathered_ticket_information = gatherAndCompactContentByClassName('comment-description') +
                                                 tailText(gatherAndCompactContentByClassName('comment'), 1024);

            const data = await LLM(gathered_ticket_information, review_systemMessage, 0.5, 4000, model);
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

    initiateChatWithSystemMessage();
})();
