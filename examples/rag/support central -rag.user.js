// ==UserScript==
// @name         Boss 4 - MessageBox GPT
// @version      0.2
// @author       Lily Rudloff
// @match        https://*/SupportCentral/HelpdeskTickets/Details/*
// @grant        none
// ==/UserScript==

var myInfoContext = {
    "My Name": "Samuel Rudloff",
    "My Job Title":"Application Programmer",
    "My Manager":"Deb Fett"
};

function extractAllCommentsDetails() {
  const commentDescriptions = document.querySelectorAll('.comment-description');
  const allCommentsDetails = [];
  commentDescriptions.forEach(commentDescription => {
    const title = commentDescription.querySelector('.title').textContent.trim();
    const nameAnchor = commentDescription.querySelector('.name > a');
    const name = nameAnchor.textContent.trim();
    const profileLink = nameAnchor.href.trim();
    const reportedTime = commentDescription.querySelector('.name > time').textContent.trim();
    const sourceText = commentDescription.querySelector('.name').textContent.trim();
    const source = sourceText.match(/Source: (.+)/)[1];
    const descParagraphs = commentDescription.querySelectorAll('.desc, .x_xxxxxmsonormal');
    const description = Array.from(descParagraphs).map(p => p.textContent.trim()).join(' ');
    const commentDetails = { title, name, profileLink, reportedTime, source, description };
    allCommentsDetails.push(commentDetails);
  });
  return allCommentsDetails;
}

function extractRequesterDetails() {
  const ticketRequester = document.querySelector('.ticket-requester');
  const nameAnchor = ticketRequester.querySelector('.title > a');
  const name = nameAnchor.textContent.trim();
  const phoneAnchor = ticketRequester.querySelector('.contact > a[href^="tel:"]');
  const phone = phoneAnchor.textContent.trim();
  const emailAnchor = ticketRequester.querySelector('.contact > a[href^="mailto:"]');
  const email = emailAnchor.textContent.trim();
  const additionalInfoDl = ticketRequester.querySelector('.additional-info .dl-horizontal');
  const additionalInfo = {};
  const dts = additionalInfoDl.querySelectorAll('dt');
  const dds = additionalInfoDl.querySelectorAll('dd');
  dts.forEach((dt, index) => {
    const key = dt.textContent.trim();
    const value = dds[index].textContent.trim();
    additionalInfo[key] = value;
  });
  const details = { name, phone, email, additionalInfo };
  return details;
}

function extractTicketDetails() {
  const commentDescription = document.querySelector('.comment-description');
  const title = commentDescription.querySelector('.title').textContent.trim();
  const nameAnchor = commentDescription.querySelector('.name > a');
  const name = nameAnchor.textContent.trim();
  const reportedTime = commentDescription.querySelector('.name > time').textContent.trim();
  const reportedTimeTooltip = commentDescription.querySelector('.name > time').getAttribute('data-original-title').trim();
  const sourceText = commentDescription.querySelector('.name').textContent.trim();
  const source = sourceText.match(/Source: (.+)/)[1];
  const descParagraphs = commentDescription.querySelectorAll('.desc, .x_MsoNormal');
  const description = Array.from(descParagraphs).map(p => p.textContent.trim()).join(' ');
  const commentDetails = { title, name, reportedTime, reportedTimeTooltip, source, description };
  return commentDetails;
}

function convertNewlinesToBrTags(str) {
  if (typeof str !== 'string') {
    return '';
  }
  return str.replace(/\n/g, '<br>');
}

function printDictionary(dictionary) {
  const formattedEntries = Object.entries(dictionary).map(([key, value]) => `${key}=${value}`);
  const output = formattedEntries.join('\n');
  return output;
}

function showModal() {
  let modal = document.getElementById("gpt-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "gpt-modal";
    modal.classList.add("modal", "fade");
    modal.tabIndex = -1;
    modal.setAttribute("aria-hidden", "true");
    document.body.appendChild(modal);
  }
  modal.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
          <h4 class="modal-title">Response Tool</h4>
        </div>
        <div class="modal-body">
          <textarea class="form-control" rows="5" style="width: 100%; margin-bottom: 10px;" id='gpt-input'></textarea>
          <button type="button" class="btn btn-primary" style="width: 100%; margin-bottom: 10px;" id="gpt-transform">Generate Response</button>
          <div id="gpt-response-container" style="display: none;">
            <textarea class="form-control" rows="13" style="width: 100%;" id='gpt-output'></textarea>
            <hr>
            <button type="button" class="btn btn-success" style="width: 100%; margin-bottom: 10px;" id="gpt-accept">Accept Response</button>
          </div>
        </div>
      </div>
    </div>
  `;
  $(modal).modal({
    backdrop: 'static',
    keyboard: false
  });
  return modal;
}

async function GenerateAiResponse(ticket_id, system_message, query) {
  const url = "http://localhost:11435/api/rag";
  const data = {
    "prompt": query,
    "system_message": system_message,
    "model": "interstellarninja/hermes-2-theta-llama-3-8b",
    "related_count": 20,
    "max_tokens": 100,
    "embeddings_db": "TicketEmbeddings_" + String(ticket_id),
    "temperature": 0.9
  };
  const headers = {
    "Content-Type": "application/json"
  };
  const response = await fetch(url, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(data)
  });
  const result = await response.json();
  return result.message.content;
}

setTimeout(function() {
  'use strict';
  var customButtonMarkup = `
    <div class="note-btn-group btn-group note-gpt">
      <button type="button" class="note-btn btn btn-default btn-sm" role="button">
        <i class="s7-gleam"></i>
      </button>
    </div>
  `;

  var toolbar = document.querySelector('.note-toolbar');
  while (!toolbar){
    toolbar = document.querySelector('.note-toolbar');
  }
  if (toolbar) {
    console.log("injected")
    toolbar.insertAdjacentHTML('beforeend', customButtonMarkup);
  } else {
    console.log("failed to inject")
  }

  var customButton = document.querySelector('.note-gpt .note-btn');
  if (customButton) {
    customButton.addEventListener('click', async function() {
      $("#gpt-response-container").hide();
      let modal = showModal();

      var htmlContent = $(".summernote-textarea").summernote('code');
      var tempElement = $('<div>').html(htmlContent);
      $("#gpt-input").val(tempElement.text());
      $("#gpt-input").focus();
      $("#gpt-accept").click(function(){
        $(".summernote-textarea").summernote('code',convertNewlinesToBrTags($("#gpt-output").val()));
        $("#gpt-modal").modal("hide");
      });
      $("#gpt-transform").click(async function(){
        var v = $("#gpt-transform");
        v.addClass("disabled");
        v.text("Loading...");
        $("#gpt-accept").addClass('disabled');

        var textContent = $("#gpt-input").val();
        var systemMessage = `Here are the rules:
1. The recipient knows my name already, do not introduce me!
2. You are acting as the user creating a comment in their support ticket.
3. You will correct any conduct issues in the supplied text, please reword it in your own words.
4. Please try and write professionally but do not be formal.
5. Your message should be concise, don't share all the info you know.

Context:
Requester Info in json format:
${JSON.stringify(extractRequesterDetails())}

Technitian  Info:
${printDictionary(myInfoContext)}
please take the next message as your directions from the technician on how to write the message.`;

        try {
          const response = await GenerateAiResponse('some_ticket_id', systemMessage, textContent);
          v.removeClass("disabled");
          v.text("Generate Response");
          $("#gpt-response-container").show();
          $("#gpt-accept").removeClass('disabled');
          $("#gpt-output").val(response);
        } catch (error) {
          v.removeClass("disabled");
          v.text("Generate Response");
          console.error("Error generating response:", error);
        }
      });
    });
  }
}, 5);
