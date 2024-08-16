// ==UserScript==
// @name         Boss 4 - Magic Notes
// @namespace    http://tampermonkey.net/
// @version      2024-05-09
// @description  Try to take over the world!
// @author       You
// @match        https://itsm.ingham.org/SupportCentral/HelpdeskTickets/Details/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';
    const ticket_id = document.location.href.split('/')[6].split('?')[0];


    async function insertTextEmbeddings(embeddingRequest) {
        const url = 'http://localhost:11435/api/embeddings/insert_text_embeddings/';

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(embeddingRequest)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Response data:', data);
            return data;
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    }






function insertNote(query, note){
    const embeddingRequest = {
        source: query + " #sr-" + ticket_id,
        content: note,
        overlap: 0,
        chunk_size: 9999,
        check_existing: true,
        embeddings_db: "Boss4-MagicNotes"
    };
    insertTextEmbeddings(embeddingRequest)
    .then(response => {
        // Handle the response here
        console.log('Embeddings inserted successfully:', response);
    })
    .catch(error => {
        // Handle any errors here
        console.error('Error inserting embeddings:', error);
    });

}




async function fetchEmbeddingsSearch(content, maxRelated, minimalSimilarity) {
    const requestData = {
        embeddings_db: "Boss4-MagicNotes", // Required field
        query: null, // Optional field, make sure it's null or a string
        queries: content, // Optional field, should be an array of strings
        max_related: maxRelated, // Required field
        minimal_similarity: minimalSimilarity // Required field
    };

    const response = await fetch('http://localhost:11435/api/embeddings/search_embeddings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return await response.json();
}




function setupFormEvents(){
// form submission functions
    $('#insert_note').click(function(){
        var query = $('#additional_query').val();
        var note = $('#note_input').val();
        if (note == ""){
            alert("Please fill out note")
            return
        }
        if (query != ""){
            insertNote(query, note);
        }

        var requestor = document.querySelector("div.ticket-requester.mb-20").querySelector('a').textContent
        var title = document.querySelector("div.comment-description > div.text > p.title").textContent
        insertNote(requestor, note);
        insertNote(title, note);
    });

}





function transformEmbeddingsToContentGroups(embeddings){
    var existing_contents = {}
    for (let i = 0; i < embeddings.length; i++) {
        if (existing_contents.hasOwnProperty(embeddings[i].content)){
            existing_contents[embeddings[i].content].push(embeddings[i].source)
        }else{
            existing_contents[embeddings[i].content] = [embeddings[i].source]
        }
    }
    return existing_contents
}

function transformEmbeddingsToRowItem(embedding){
    //info icon with hover of list of all related sources, next to content
    var sources = embedding.source.join("\n ")
    return `<tr><td>${embedding.content} <span title="${sources}" data-tooltip="" title="" data-placement="top">🛈</span></td></tr>`
}





    // Call the function with a ticket ID of 1
    async function initiateSystem() {
        try {
            var requestor = document.querySelector("div.ticket-requester.mb-20").querySelector('a').textContent
            var title = document.querySelector("div.comment-description > div.text > p.title").textContent
            var query_requestor = requestor
            var query_title = title
            // Example usage
            var queries = [query_requestor, query_title];
            fetchEmbeddingsSearch(queries, 100, 0.2)
            .then(relatedEmbeddings => {
                console.log('Related Embeddings:', relatedEmbeddings);




                document.querySelector("#magicnotes_loading_id").remove();
                let output = "<div><strong>Queryies:</strong>";
                output += `<p>${query_requestor}</p>`;
                output += `<p>${query_title}</p>`;
                output += "</div>";
                output += `<table width="100%" id='magic_notes_table'>`;
                output += `<thead><tr><th>AI Notes</th></tr></thead>`;
                output += `<tbody>`;

                var existing_contents = transformEmbeddingsToContentGroups(relatedEmbeddings)
                for (const [key, value] of Object.entries(existing_contents)) {
                    output += transformEmbeddingsToRowItem({content: key, source: value})
                }
                //note input area, Additional Input Query,multiline edit, insert button


                output += `</tbody>`;
                output += `<tfoot>`;
                output += `<tr style='background-color: #f2f2f2;'><td></td></tr>`;
                output += `<tr style='background-color: #f2f2f2;'><td><input type='text' placeholder='additional note title' id='additional_query'/><br><textarea id="note_input" rows="4" cols="50"></textarea></td></tr>`;
                output += `<tr style='background-color: #f2f2f2;'><td><button id="insert_note">Insert Note</button></td></tr>`;


                output += `</tfoot>`;
                output += `</table>`;
                $('#magicnotes_output').append(output);
                setupFormEvents();
            });

        } catch (error) {
            console.error('Error during chat initiation:', error);
            $('#magicnotes_output').append("Error Inializing: " + error + "<br>")
            $('#magicnotes_output').css("background-color", "rgb(251 204 204)")
        }
    }

    // Create a style element
    var style = document.createElement('style');
    document.head.appendChild(style);
    style.innerHTML = `
        #magicnotes_output::before {
            content: "Ai Notes";
            position: absolute;
            top: 0;
            left: 0;
            text-align: left;
            border-bottom-right-radius: 15px;
            border-bottom: 2px #d95050 solid;
            border-right: 2px #d95050 solid;
            padding: 3px 7px 3px 3px;
        }
        #magicnotes_output {
            position: relative;
            text-align:left;
            width: 100%;
            background-color: lightgoldenrodyellow;
            padding: 25px;
            padding-top:45px;

        }
        #magic_notes_table {
            width: 100%;                /* Ensure the table takes full width */
            border-collapse: collapse;  /* Ensures borders between cells are collapsed into a single border */
            table-layout: auto;         /* Allow the table to automatically adjust column widths */
        }

        #magic_notes_table th,
        #magic_notes_table td {
            padding: 8px;               /* Standard padding within cells */
            border: 1px solid black;    /* Standard border for readability */
            text-align: left;           /* Align text to the left within cells */
        }

        #magic_notes_table tbody tr:nth-child(even) {
            background-color: #f2f2f2;  /* Light gray background for even rows, for better readability */
        }
        #magic_notes_table textarea {
            width: 100%;
        }
        #magic_notes_table input {
            width: 100%;
        }
    `;


    $('.comment-description').append(`
        <div style="" id="magicnotes_output">
            <center id="magicnotes_loading_id">Loading AI Notes...</center>
        </div>
    `);
    initiateSystem();
})();
