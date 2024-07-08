// ==UserScript==
// @name         Ticket System 4 - AI Next Reply
// @namespace    http://tampermonkey.net/
// @version      2024-05-09
// @description  Try to take over the world!
// @author       You
// @match        https://*/HelpdeskTickets/Details/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    const model = 'dolphin-mistral:latest';
    const now = new Date();
    const date = now.toLocaleDateString();
    const formattedDateTime = `${date}`;

    const review_systemMessage = `
Todays Dateis ${formattedDateTime},we are playing a game, The game is called "Dont stick out"
We are playing as It Support

Here are the game rules:
1. dont say the default format elements;
2. dont ask for information a programmer would already know, be casual.Never be egotistial or sarcastic.
3. use brief replies, keep it professional and deesclate as much as possible.
4. dont let them know you are an AI
5. users are not technical and i will more than likely be remoting into their computers to solve the issue.
6. no pleasentries statements like "I hope this message finds you well.
7. dont provide contact details

remember, we are playing a game, the point is to blend in and not stick out. Good luck!
"
    `;

    async function LLM(prompt, systemMessage, temperature, max_tokens, model) {
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
                    return_json: false
                })
            });
            const data = await response.json();
            console.log('Success:', data);
            $('#reply_loading_id').remove();
            return data;
        } catch (error) {
            console.error('Error:', error);
            $('#reply_loading_id').remove();
            $('#ai_reply_output').append("Error with llm: " + error+"<br>")
            $('#ai_reply_output').css("background-color","rgb(251 204 204)")
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
   
function headText(text, length) {
    return text.slice(0, length);
}
    // Call the function with a ticket ID of 1
    async function initiateSystem() {
        try {
            const gathered_ticket_information = headText(gatherAndCompactContentByClassName('comment-description'),724)
            const requestor_data = {
                'name':document.querySelector("div.ticket-requester.mb-20").querySelector('a').textContent
            }
            const gathered_ticket_comments =tailText(gatherComments(),3048)
            const ticket_id = document.location.href.split('/')[6].split('?')[0];
            const query = `
            Requestor Information:
            ${JSON.stringify(requestor_data)}


            Ticket Information:
            ${gathered_ticket_information}


            COMMENTS
            ${gathered_ticket_comments}
            `;
            const data = await LLM(query, review_systemMessage, 0.97, 24000, model);
            if (!data || !data.message || !data.message.content) {
                $('#ai_reply_output').html("AI Offline")
                console.log(data)
                $('#ai_reply_output').css("background-color","rgb(251 204 204)")
                return;
            }
            let output = "";
            output = `<p>${data.message.content.replace('\n','<br>')}</p>`;
            $('#ai_reply_output').append(output);
        } catch (error) {
            console.error('Error during chat initiation:', error);
            $('#ai_reply_output').append("Error Inializing: " + error + "<br>")
            $('#ai_reply_output').css("background-color","rgb(251 204 204)")
        }
    }

  // Create a style element
    var style = document.createElement('style');
    document.head.appendChild(style);
    style.type = 'text/css';
    style.innerHTML = `
        #ai_reply_output::before {
    content: "Ai Reply";
    position: absolute;
    top: 0;
    left: 0;
    text-align: left;
    border-bottom-right-radius: 15px;
    border-bottom: 2px #d95050 solid;
    border-right: 2px #d95050 solid;
    padding: 3px 7px 3px 3px;
}
        #ai_reply_output {
            position: relative;
            text-align:left;
            width: 100%;
            background-color: pink;
            padding: 25px;
            padding-top:45px;

        }
    `;


    $('.comment-description').append(`
        <div style="" id="ai_reply_output">
            <center id="reply_loading_id">Loading AI Reply Output...</center>
        </div>
    `);
    initiateSystem();
})();
