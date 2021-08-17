(async () => {
  if ("undefined" != typeof isSupervisorPage && !!isSupervisorPage) {
    const zulip = require("zulip-js");

    const supervisorEmail = localStorage.getItem("supervisor_email");
    const apiKey = localStorage.getItem("key");
    const stream_name = localStorage.getItem("stream_name");

    const pollyImg = document.getElementById("polly-img").value;
    const clientImg = document.getElementById("client-img").value;
    const supervisorImg = document.getElementById("supervisor-img").value;

    // Listen 'Enter' key press
    $(document).on("keyup", "#message-text", (event) => {
      if (event.keyCode === 13) {
        event.preventDefault();
        event.target.blur();
        document.getElementById("send-message-btn").click();
      }
    });

    let index; // botui message id

    const renderSupervisorMessage = async (event) => {
      switch (event.type) {
        case "typing":
          if (event.sender.email !== supervisorEmail) {
            if (event.op === "start") {
              index = await botui.message.add({
                loading: true,
                human: false,
              });
            } else {
              await botui.message.remove(index, {
                loading: false,
                human: false,
              });
            }
          }
          break;
        case "message":
          if (event.message.sender_email !== supervisorEmail) {
            if (event.message.type === "stream") {
              const photo =
                event.message.sender_email === staffEmail
                  ? pollyImg
                  : clientImg;
              await botui.message.add({
                loading: false,
                human: false,
                photo: photo,
                content: event.message.content,
              });
            }
          }
          break;
        default:
          console.log("event", event);
      }
    };

    const config = {
      username: supervisorEmail,
      apiKey: apiKey,
      realm: zulipRealm,
    };
    const client = await zulip(config);

    const handleEvent = async (event) => {
      console.log("Got Event:", event);
      renderSupervisorMessage(event);
    };

    // send message
    $(document)
      .on("click", "#send-message-btn", async () => {
        const text = document.getElementById("message-text");
        if (!text.value) {
          text.focus();
          return;
        }

        botui.message.human({
          photo: supervisorImg,
          content: text.value,
        });

        const params = {
          to: stream_name,
          type: "stream",
          topic: "chat",
          content: text.value,
        };
        await client.messages.send(params);

        text.value = "";
        // text.focus();
      })
      .on("click", "#stream-leave-chatroom-btn", async () => {
        const result = confirm("Are you sure you want to leave the chatroom?");
        if (result == true) {
          const response = await $.ajax({
            url: "/main/chat/unsubscribe_stream/",
            method: "POST",
            dataType: "json",
            data: JSON.stringify({
              unsubscribers_netid: [supervisor_netid],
              staff_netid: staffNetid,
            }),
          });

          if (response.status == "success") {
            document.getElementById("send-message-div").style.visibility =
              "hidden";
            alert("You have successfully left the conversation.");
          } else {
            alert("Ops, Something wrong happened.");
          }
        }
      })
      .on("focus", "#message-text", async () => {
        await client.typing.send({
          type: "stream",
          to: [stream_id],
          op: "start",
          topic: "chat",
        });
      })
      .on("blur", "#message-text", async () => {
        await client.typing.send({
          type: "stream",
          to: [stream_id],
          op: "stop",
          topic: "chat",
        });
      })
      .on("click", ".icon-leave", function() {
        if (confirm("Are you sure you want to quit?")) {
          if (
            navigator.userAgent.indexOf("Firefox") != -1 ||
            navigator.userAgent.indexOf("Chrome") != -1
          ) {
            window.location.href = "about:blank";
            window.close();
          } else {
            window.opener = null;
            window.open("", "_self");
            window.close();
          }
        }
      })
      .on("click", ".icon-home", function() {
        location.reload();
      });

    try {
      await client.callOnEachEvent(handleEvent, ["streams"]);
    } catch (error) {
      console.log("error", error.message);
    }
  }
})();
