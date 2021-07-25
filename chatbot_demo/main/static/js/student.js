(async () => {
  if (isStudentPage) {
    const zulip = require("zulip-js");

    // const isStudent = localStorage.getItem("is_student");
    // const studentEmail = localStorage.getItem("student_email");
    // const apiKey = localStorage.getItem("key");

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

    // student
    let index; // botui message id
    // let streamName = "";
    // let staffEmail = "";

    // hide the input area in case student send a message before connecting to a counsellor
    // const chatDiv = document.getElementById("send-message-div");
    // chatDiv.style.visibility = "hidden";

    // render student message when there is a event received
    const renderStudentMessage = async (event) => {
      switch (event.type) {
        case "typing":
          if (event.sender.email !== studentEmail) {
            if (event.op === "start") {
              index = await botui.message.add({
                loading: true,
                human: false,
                photo: pollyImg,
              });
            } else {
              await botui.message.remove(index, {
                loading: false,
                human: false,
                photo: pollyImg,
              });
            }
          }
          break;
        case "message":
          if (event.message.sender_email !== studentEmail) {
            if (event.message.type === "stream") {
              // append the message
              const photo =
                event.message.sender_email === staffEmail
                  ? pollyImg
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
        // case "stream":
        //   if (event.op === "delete") {
        //     await botui.message.add({
        //       loading: false,
        //       human: false,
        //       photo: pollyImg,
        //       content: "Thank you for using our service. Goodbye.",
        //     });
        //   }
        //   break;
        case "subscription":
          if (event.op === "remove") {
            await botui.message.add({
              loading: false,
              human: false,
              photo: pollyImg,
              content: "Thank you for using our service. Goodbye.",
            });

            // staffEmail = "";
            document.getElementById("send-message-div").style.visibility =
              "hidden";
          }
        default:
          console.log("event default", event);
      }
    };

    const config = {
      username: studentEmail,
      apiKey: apiKey,
      realm: "https://zulip.cat",
    };
    const client = await zulip(config);

    const handleEvent = async (event) => {
      console.log("Got Event:", event);
      renderStudentMessage(event);
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
          photo: clientImg,
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
      .on("focus", "#message-text", async () => {
        await client.typing.send({
          // TODO update recipient
          to: [staffEmail],
          op: "start",
        });
      })
      .on("blur", "#message-text", async () => {
        await client.typing.send({
          to: [staffEmail],
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
