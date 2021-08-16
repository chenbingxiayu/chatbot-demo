(async () => {
  if ("undefined" != typeof isCounsellorPage && isCounsellorPage) {
    const zulip = require("zulip-js");

    const pollyImg = document.getElementById("polly-img").value;
    const clientImg = document.getElementById("client-img").value;
    const supervisorImg = document.getElementById("supervisor-img").value;

    function debounce(func, delay) {
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
          func.apply(this, args);
        }, delay);
      };
    }

    let index; // botui message id

    const renderCounsellorMessage = async (event) => {
      switch (event.type) {
        case "typing":
          if (event.sender.email !== staffEmail) {
            if (event.op === "start") {
              index = await botui.message.add({
                loading: true,
                human: false,
                photo: clientImg,
              });
            } else {
              await botui.message.remove(index, {
                loading: false,
                human: false,
                photo: clientImg,
              });
            }
          }
          break;
        case "message":
          if (event.message.sender_email !== staffEmail) {
            if (event.message.type === "stream") {
              const photo =
                event.message.sender_email === studentEmail
                  ? clientImg
                  : supervisorImg;
              await botui.message.add({
                loading: false,
                human: false,
                photo: photo,
                content: event.message.content,
              });
            }
          }
          break;
        case "subscription":
          // remove student
          if (
            event.op == "peer_remove" &&
            !event.subscriptions.includes(studentEmail)
          ) {
            studentEmail = "";
          }
          break;
      }
    };

    const config = {
      username: staffEmail,
      apiKey: apiKey,
      realm: zulipRealm,
    };
    const client = await zulip(config);

    const handleEvent = async (event) => {
      console.log("Got Event:", event);
      renderCounsellorMessage(event);
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
          photo: pollyImg,
          content: text.value,
        });

        const params = {
          to: streamName,
          type: "stream",
          topic: "chat",
          content: text.value,
        };

        await client.messages.send(params);

        text.value = "";
      })
      // Listen 'Enter' key press
      .on("keyup", "#message-text", (event) => {
        if (event.keyCode === 13) {
          event.preventDefault();
          event.target.blur();
          document.getElementById("send-message-btn").click();
        }
      })
      .on("click", ".counsellor-leave-chatroom-btn", async (event) => {
        const result = confirm(
          "Are you sure you want to end the conversation?"
        );
        if (result == true) {
          const unsubscribePromise = $.ajax({
            url: "/main/chat/unsubscribe_stream/",
            method: "POST",
            dataType: "json",
            data: JSON.stringify({
              unsubscribers_netid: [studentNetid],
              staff_netid: staffNetid,
            }),
          });

          const deleteChatHistoryPromise = $.ajax({
            url: "/main/chat/delete_stream_in_topic/",
            method: "POST",
            dataType: "json",
            data: JSON.stringify({
              staff_netid: staffNetid,
            }),
          });

          console.log("is no show", $(event.target).hasClass("no-show"));

          // debug/endchat/
          const endChatPromise = $.ajax({
            url: "/main/debug/endchat/",
            method: "POST",
            data: {
              staff_netid: staffNetid,
              student_netid: studentNetid,
              is_no_show: $(event.target).hasClass("no-show"),
            },
          });

          try {
            const results = await Promise.all([
              unsubscribePromise,
              deleteChatHistoryPromise,
              endChatPromise,
            ]);
            const hasError = !!results.find(
              (result) => result.status !== "success"
            );
            if (hasError) {
              throw new Error(results);
            }
            console.log("Successfully delete the history");
            alert("You have successfully end the conversation.");
          } catch (error) {
            console.log(error);
            alert("Ops, Something wrong happened.");
          }
        }
      })
      .on("focus", "#message-text", async () => {
        if (!studentEmail) {
          return;
        }

        await client.typing.send({
          to: [studentEmail],
          op: "start",
        });
      })
      .on("blur", "#message-text", async () => {
        if (!studentEmail) {
          return;
        }

        await client.typing.send({
          to: [studentEmail],
          op: "stop",
        });
      });

    try {
      await client.callOnEachEvent(handleEvent, ["streams"]);
    } catch (error) {
      console.log("error", error.message);
    }
  }
})();
