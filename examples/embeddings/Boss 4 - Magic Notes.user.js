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
        requestor = clean_string(requestor);
        title = clean_string(title);
        // Example usage
        var queries = [requestor, title, extractSubject(),extractWeirdSubject()];
        queries = deduplicate_queries(queries)
        for (let i = 0; i < queries.length; i++) {
            insertNote(queries[i], note);
        }
    });

}
function extractSubject() {
    var des_lines = document.querySelector('.desc').textContent.split('\n');
    let subject = null;
    des_lines.forEach(line => {
        if (line.includes("Subject:")) {
            line = line.replace("::", ":");
            subject = line.split(":")[1].trim();
        }
    });
    return clean_string(subject);
}
function clean_string(subject){
    if (subject == null){
        return ""
    }
    //remove all punctuation
    subject = subject.replace("-", " ");
    subject = subject.replace(":", " ");
    subject = subject.replace(";", " ");
    subject = subject.replace(",", " ");
    subject = subject.replace(".", " ");
    subject = subject.replace("!", " ");
    subject = subject.replace("?", " ");
    subject = subject.replace("(", " ");
    subject = subject.replace(")", " ");
    subject = subject.replace("[", " ");
    subject = subject.replace("]", " ");
    subject = subject.replace("{", " ");
    subject = subject.replace("}", " ");
    subject = subject.replace("'", " ");
    subject = subject.replace('"', " ");
    subject = subject.replace("`", " ");
    subject = subject.replace("~", " ");
    subject = subject.replace("$", " ");
    subject = subject.replace("%", " ");
    subject = subject.replace("^", " ");
    subject = subject.replace("*", " ");
    subject = subject.replace("=", " ");

    subject = subject.replace("  ", " ");
    
    subject = subject.trim();

    subject = subject.toLowerCase();


    return subject;
}

function deduplicate_queries(queries){
    var uniqueQueries = []
    queries.forEach(query => {
        if (query != null && !uniqueQueries.includes(query)){
            uniqueQueries.push(query)

        }
        // case insensitive
        else if (query != null && !uniqueQueries.includes(query.toLowerCase())){
            uniqueQueries.push(query.toLowerCase())
        }
    });
    //remove empty strings
    
    return uniqueQueries
}

function extractWeirdSubject() {
    // Extract the text content from the element with the class 'desc'
    var desLines = document.querySelector('.desc').textContent.split('\n');

    // Loop through each line of the description
    for (let line of desLines) {
        line = line.replace("::", ":");
        // Check if the line contains "Subject:"
        if (line.includes("Subject:")) {
            // Extract and clean the subject text
            let subject = line.split(":")[1].trim();
            // Return the important phrases from the subject
            return extractImportantPhrases(subject);
        }
    }
    // Return null if "Subject:" is not found
    return null;
}

function extractImportantPhrases(subject) {
    // List of key phrases to look for
    let importantPhrases = [
        // Content & Updates
        "post",
        "upload",
        "publish",
        "update",
        "migrate",
        "repair",
        "fix",
        "issue",
        "problem",
        "error",
        "fail",
        "failed",
    
        // Reports & Analytics
        "report",
        "spreadsheet",
        "analytics",
        "data",
        "results",
    
        // Communication & Email
        "email",
        "notification",
        "alert",
        "message",
        "reminder",
        "seamless docs",
    
        // Billing & Finance
        "billing",
        "invoice",
        "payment",
        "charge",
        "refund",
    
        // Website & Sharepoint
        "website",
        "html",
        "sharepoint",
        "portal",
        "webpage",
        "site"
    ];

    // Convert the subject to lowercase and split into words
    let words = subject.toLowerCase().split(/\s+/);

    // Filter the important phrases that match words in the subject
    let matchedPhrases = importantPhrases.filter(phrase => 
        phrase.split(' ').every(word => words.includes(word))
    );

    // Join the matched phrases into a single string and return
    return matchedPhrases.join(' ');
}

function transformEmbeddingsToContentGroups(embeddings){
    var existing_contents = {}
    for (let i = 0; i < embeddings.length; i++) {
        if (existing_contents.hasOwnProperty(embeddings[i].content)){
            existing_contents[embeddings[i].content].push(embeddings[i].source + " S:"+embeddings[i].query_similarity
            )
        }else{
            existing_contents[embeddings[i].content] = [embeddings[i].source + " S:"+embeddings[i].query_similarity
        ]
        }
    }
    return existing_contents
}

function transformEmbeddingsToRowItem(embedding){
    //info icon with hover of list of all related sources, next to content
    var sources = embedding.source.join("\n")
    return `<tr><td>${convert_content_to_html(embedding.content)} <span title="${sources}" data-tooltip="" title="" data-placement="top">🛈</span></td></tr>`
}

function convert_content_to_html(text){
    var urlRegex = /(https?:\/\/[^\s]+)/g;

    text = text.replace(urlRegex, function(url) {
        return '<a target="_blank" href="' + url + '">' + url + '</a>';
    })

    return text;
}



    // Call the function with a ticket ID of 1
    async function initiateSystem() {
        try {
            var requestor = document.querySelector("div.ticket-requester.mb-20").querySelector('a').textContent
            var title = document.querySelector("div.comment-description > div.text > p.title").textContent
            requestor = clean_string(requestor);
            title = clean_string(title);
            // Example usage
            var queries = [requestor, title, extractSubject(),extractWeirdSubject()];
            queries = deduplicate_queries(queries)
            fetchEmbeddingsSearch(queries, 100, 0.6)
            .then(relatedEmbeddings => {
                console.log('Related Embeddings:', relatedEmbeddings);




                document.querySelector("#magicnotes_loading_id").remove();
                let output = "<div><strong>Queries:</strong>";
                output += "<ul>";
                queries.forEach(query => {
                    output += `<li>${query}</li>`;
                });
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
