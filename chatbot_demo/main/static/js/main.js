(function () {
  $("body").on("click", ".dropdown", function () {
    $(".botui-container").animate(
      { scrollTop: $(".botui-container").prop("scrollHeight") },
      1000
    );
  });

  select_language().then(
    init_choices
    // get_name).then(T_and_C_split).then(
    // questions

    // questions

    //T_and_C_of_OCS

    // low
    // medium
    // high
  );

  function init_choices() {
    var office_hour = isSAOWorkingHours(new Date());
    if (office_hour == true) {
      return botui.message
        .bot({
          loading: true,
          delay: 1000,
          photo: polly,
          content: "Please select the service below:",
        })
        .then(function () {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Counselling Chatbot", value: 1 },
                { text: "Mental Health Educational Materials", value: 2 },
                { text: "Online Chat", value: 4 },
                { text: "Make Appointment with SAO counsellor", value: 5 },
                { text: "Immediate Contact with SAO counsellor", value: 3 },
                { text: "Emergency Support", value: 6 },
              ],
            })
            .then(function (res) {
              if (res.value == 1) {
                service_list = false;
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(get_name)
                  .then(questions);
              }
              if (res.value == 2) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(mental_health_101);
              }
              if (res.value == 3) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(contact_with_counsellors);
              }
              if (res.value == 4) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(T_and_C_of_OCS);
              }
              if (res.value == 5) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(make_appointment_with_counsellors);
              }
              if (res.value == 6) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(emergency_support);
              }
            });
        });
    } else {
      return botui.message
        .bot({
          loading: true,
          delay: 1000,
          photo: polly,
          content: "Please select the service below:",
        })
        .then(function () {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Counselling Chatbot", value: 1 },
                { text: "Mental Health Educational Materials", value: 2 },
                { text: "Make Appointment with SAO counsellor", value: 5 },
                { text: "Immediate Contact with PolyU-Line Counsellor (852) 8100 1583", value: 3 },
                { text: "Emergency Support", value: 6 },
              ],
            })
            .then(function (res) {
              if (res.value == 1) {
                service_list = false;
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(get_name)
                  .then(questions);
              }
              if (res.value == 2) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(mental_health_101);
              }
              if (res.value == 3) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(polyu_line);
              }
              if (res.value == 5) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(make_appointment_with_counsellors);
              }
              if (res.value == 6) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(emergency_support);
              }
            });
        });
    }
  }

  function isSAOWorkingHours(now) {
    var weekday = now.getDay();
    var hours = now.getHours();
    // Mon - Fri
    if (weekday >= 1 && weekday <= 5) {
      // 9:00-19:00
      if (hours >= 9 && hours < 19) {
        return true;
      }
    }

    // Sat
    if (weekday == 6) {
      // 9:00 - 12:00
      if (hours >= 9 && hours < 12) {
        return true;
      }
    }
    return false;
  }

  function select_language() {
    return botui.message
      .bot({
        photo: polly,
        loading: true,
        searchselect: true,
        delay: 1000,
        content: gettext("Please select your language 請選擇語言"),
      })
      .then(function () {
        return botui.action
          .select({
            addMessage: false,
            action: {
              placeholder: "Please select a language",
              value: "en",
              options: [
                { value: "en", text: "English" },
                { value: "zh-hant", text: "繁體中文" },
                { value: "zh-hans", text: "简体中文" },
              ],
              button: {
                icon: "check",
                label: "OK",
              },
            },
          })
          .then(function (res) {
            return botui.message.human({
              photo: client,
              delay: 500,
              content: res.text,
            });
          });
      });
  }

  function get_name() {
    return botui.message
      .bot({
        photo: polly,
        loading: true,
        delay: 3000,
        content:
          'Hello! This is Polly. I\'m here to understand your service need and provide you with appropriate services.<br/><br/>You may know more about SAO services <br/><a href="https://www.polyu.edu.hk/sao/" target ="_blank">HERE</a> ',
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 1000,
          content: "May I have your name please?",
        });
      })
      .then(function () {
        return botui.action.text({
          addMessage: false,
          action: {
            size: 30,
            placeholder: "Nickname",
          },
        });
      })
      .then(function (res) {
        name = res.value;
        return botui.message.human({
          photo: client,
          delay: 500,
          content: res.value,
        });
      });
  }

  function T_and_C_split() {
    var ESI = "";
    var office_hour = isSAOWorkingHours(new Date());
    if (office_hour == false) {
      ESI =
        '<a href="https://www.polyu.edu.hk/sao/cws/student-counselling/emergency-support/non-office-hours/" target ="_blank">Emergency support information</a>';
    } else {
      ESI =
        '<a href="https://www.polyu.edu.hk/sao/cws/student-counselling/emergency-support/office-hours/" target ="_blank">Emergency support information</a>';
    }
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 2000,
        content:
          "Hi " +
          name +
          ', you need to read the followings prior using "My Polly":</br></br>Important Notes:</br>In case of emergency and when there is an imminent hazard posed to you and others, please call 999 or go to the nearest emergency / A&E service.' +
          '</br></br>Please visit the <a target ="_blank" href="https://www.polyu.edu.hk/sao/cws/student-counselling/emergency-support/office-hours/" >HERE</a> for more emergency support information.</br></br>' +
          ESI +
          "</br>",
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            {
              text: "Got it",
            },
          ],
        });
      })
      .then(function (res) {
        return botui.message.human({
          photo: client,
          delay: 500,
          content: res.text,
        });
      })
      .then(function (res) {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<p><b>My Polly Counselling Chatbot Service</b></p>\n" +
            "<br/>\n" +
            "<p>(The Terms and Conditions are only available in English.)</p>\n" +
            "<br/>\n" +
            "<p><b>Use of this service</b></p>\n" +
            "<p>Initiated by the SAO Counselling & Wellness Section (CWS), My Polly Counselling Chatbot Service (the “Service”) is available to all registered students of The Hong Kong Polytechnic University (the “University”) aged 18 or above.</p>\n" +
            "<br/>\n" +
            "<p>This Chatbot serves the purpose of identifying students’ service need and the referral of psychological services, ie online chat/ face-to- face counselling / online psychoeducation materials/ Non-office-hour counseling (non-crisis) / Community helplines. </p>\n",
        });
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            {
              text: "Read more",
            },
          ],
        });
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<br/>\n" +
            "<p>The Service intends to render 'remote' support through the secured online communication. However, limitation in using the Service may exist due to a number of factors, such as technical issues (both hardware and software), instability of internet connections and lack of direct interaction. The overall service quality and user experience may thereby be affected. If possible, staff of CWS may contact with the user for the service follow-up whenever necessary. </p>\n" +
            "<br/>\n" +
            "<p>The staff of CWS will follow its protocol in providing the Service. By accepting the Service, the user of the Service shall comply with the crisis protocol suggested by the staff of CWS including calling 999, notifying police and seeking help from emergency hospital services.</p>\n",
        });
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            {
              text: "Read more",
            },
          ],
        });
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<br/>\n" +
            "<p>There are situations that the staff of CWS is ethically obligated to take actions to protect the user or others from harm including disclosing the personal particulars of the user of the Service to the extent necessary. These may include contacting family members, assisting hospitalization, notifying any potential victim(s) or the police. To the extent practicable, CWS will discuss with the user prior taking such actions.</p>\n" +
            "<br/>\n" +
            "<p>There will be no guarantee of any expected results or outcome from the Service. Service user shall not hold CWS responsible for the acts of the Service user. </p>\n" +
            "<br/>\n" +
            "<p>To protect the confidentiality of the service and service users, please do not make record of service in any form. </p>\n" +
            "<br/>\n" +
            '<p>You may look into the Privacy Policy Statement of PolyU <a href="https://www.polyu.edu.hk/privacy-policy-statement/" target="_blank">HERE</a>. </p>\n' +
            "<br/>\n" +
            '<p>As for the Personal Information Collection Statement, please click <a href="https://www.polyu.edu.hk/ar/web/en/pics/index.html" target="_blank">HERE</a>.</p>',
        });
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 5000,
          content:
            'By clicking "Hi, Polly" to accept the above terms and conditions.',
        });
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            { text: "No, I stop here.", value: false },
            { text: "Hi, Polly", value: true },
          ],
        });
      })
      .then(function (res) {
        if (res.value == false) {
          return botui.message
            .bot({
              loading: true,
              photo: polly,
              delay: 2000,
              content:
                "You are always welcome to contact SAO counsellors at (852)27666800 for enquiries.",
            })
            .then(end);
        } else {
          return botui.message.bot({
            human: true,
            photo: client,
            content: res.text,
          });
        }
      });
  }

  function questions() {
    botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 1500,
        content:
          "Hi, " +
          name +
          ". To know you better, please answer a few questions below. So I can provide you with the right support.<br/><br/> It is not supposed to treat as formal psychological or diagnostic assessment.",
      })
      .then(function () {
        botui.message
          .bot({
            loading: true,
            delay: 1500,
            photo: polly,
            content:
              "Q1. What bring(s) you here to chat with us? (Can select more than one item)",
          })
          .then(q1_ans);
      });
  }

  function q1_ans() {
    $(".botui-container").animate(
      { scrollTop: $(".botui-container").prop("scrollHeight") },
      1000
    );
    return botui.action
      .select({
        addMessage: false,
        action: {
          placeholder: "Select a option",
          multipleselect: true,
          options: [
            { text: "Academic" },
            { text: "Relationship" },
            { text: "Career" },
            { text: "Family" },
            { text: "Mental Health" },
            { text: "Other" },
          ],
          button: {
            icon: "check",
            label: "OK",
          },
        },
      })
      .then(function (res) {
        if (res.text == "") {
          alert("You have to select at least one item!");
          q1_ans();
        } else {
          answers[1] =
            'Q1. What bring(s) you here to chat with us? (Can select more than one item)<br/><b><font color="#FF0000">' +
            res.text +
            "</font></b><br/>";
          return botui.message
            .human({
              photo: client,
              delay: 500,
              content: res.text,
            })
            .then(function () {
              return botui.message.bot({
                loading: true,
                delay: 1000,
                photo: polly,
                content:
                  "I see, you are now facing the issue(s) comprising " +
                  res.text +
                  ".",
              });
            })
            .then(q2);
        }
      });
  }

  function q2() {
    botui.message
      .bot({
        loading: true,
        delay: 1500,
        photo: polly,
        content:
          "Q2. With the issue(s) indicated, are you sad, worried or tensed now?",
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [
              { text: "Yes", value: 1 },
              { text: "No", value: 0 },
            ],
          })
          .then(function (res) {
            answers[2] =
              'Q2. With the issue(s) indicated, are you sad, worried or tensed now?<br/><b><font color="#FF0000">' +
              res.text +
              "</font></b><br/>";
            if (res.value == 0) {
              return botui.message
                .human({
                  photo: client,
                  delay: 500,
                  content: res.text,
                })
                .then(function (res) {
                  return botui.message
                    .bot({
                      loading: true,
                      delay: 1500,
                      photo: polly,
                      content:
                        'Keep it up! We encourage you to take a look at the "Mental Health 101" to know more tips for enhancing your psychological and mental wellness.',
                    })
                    .then(mental_health_101);
                });
            }
            score += res.value;
            console.log(score);
            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(function () {
                return botui.message.bot({
                  loading: true,
                  delay: 1500,
                  photo: polly,
                  content:
                    "Thanks for telling me. It is natural for us to experience these feelings in our daily life.",
                });
              });
          });
      })
      .then(q3);
  }

  function q3() {
    botui.message
      .bot({
        loading: true,
        delay: 1500,
        photo: polly,
        content: "Q3. How often do you feel sad, worried or tensed?",
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [
              { text: "Rarely", value: 1 },
              { text: "Seldom", value: 2 },
              { text: "Sometimes", value: 3 },
              { text: "Often", value: 4 },
              { text: "Always", value: 5 },
            ],
          })
          .then(function (res) {
            answers[3] =
              'Q3. How often do you feel sad, worried or tensed?<br/><b><font color="#FF0000">' +
              res.text +
              "</font></b><br/>";
            score += res.value;
            console.log(score);

            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(function () {
                return botui.message
                  .bot({
                    delay: 2500,
                    loading: true,
                    photo: polly,
                    content:
                      "Awareness is the first step of change that helps to aid our self-understanding and steps of healing to take.",
                  })
                  .then(function () {
                    return botui.message.bot({
                      delay: 1000,
                      loading: true,
                      photo: polly,
                      content:
                        "I see that you are aware of what is happening to you. ",
                    });
                  });
              });
          });
      })
      .then(q4);
  }

  function q4() {
    botui.message
      .bot({
        loading: true,
        delay: 2000,
        photo: polly,
        content:
          "Q4. How often does your daily life being affected by the feelings mentioned above?",
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [
              { text: "Rarely", value: 1 },
              { text: "Seldom", value: 2 },
              { text: "Sometimes", value: 3 },
              { text: "Often", value: 4 },
              { text: "Always", value: 5 },
            ],
          })
          .then(function (res) {
            answers[4] =
              'Q4. How often does your daily life being affected by the feelings mentioned above?<br/><b><font color="#FF0000">' +
              res.text +
              "</font></b><br/>";
            score += res.value;
            console.log(score);
            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(function () {
                return botui.message.bot({
                  loading: true,
                  photo: polly,
                  delay: 1500,
                  content:
                    "It shows that your daily life is being affected by these feelings.",
                });
              });
          });
      })
      .then(q5_q6);
  }

  function q5_q6() {
    botui.message
      .bot({
        loading: true,
        delay: 2500,
        photo: polly,
        content:
          "Q5. Have you been trying to cope with your feelings through positive ways? (e.g. practising physical exercise, deep breathing, listening to music, etc.)",
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [
              { text: "Yes", value: 0 },
              { text: "No", value: 1 },
            ],
          })
          .then(function (res) {
            answers[5] =
              'Q5. Have you been trying to cope with your feelings through positive ways? (e.g. practising physical exercise, deep breathing, listening to music, etc.)? (e.g. practising physical exercise, deep breathing, listening to music, etc.)<br/><b><font color="#FF0000">' +
              res.text +
              "</font></b><br/>";
            score += res.value;
            console.log(score);
            botui.message.human({
              photo: client,
              delay: 500,
              content: res.text,
            });
            if (res.value == 0) {
              return botui.message
                .bot({
                  loading: true,
                  delay: 2000,
                  photo: polly,
                  content:
                    "It is crucial to adopt some positive coping strategies in dealing with the unsettled emotions.",
                })
                .then(function () {
                  return botui.message
                    .bot({
                      loading: true,
                      delay: 1500,
                      photo: polly,
                      content:
                        "Q6. Do you feel effective when using these coping strategies?",
                    })
                    .then(function () {
                      return botui.action
                        .button({
                          addMessage: false,
                          action: [
                            { text: "Yes", value: 0 },
                            { text: "No", value: 1 },
                          ],
                        })
                        .then(function (res) {
                          answers[6] =
                            'Q6. Do you feel effective when using these coping strategies?<br/><b><font color="#FF0000">' +
                            res.text +
                            "</font></b><br/>";
                          score += res.value;
                          console.log(score);
                          botui.message.human({
                            photo: client,
                            delay: 500,
                            content: res.text,
                          });
                        });
                    });
                });
            } else {
              return botui.message
                .bot({
                  loading: true,
                  delay: 2000,
                  photo: polly,
                  content:
                    "It is crucial to find some positive coping strategies in dealing with the unsettled sadness/worry or tension",
                })
                .then(function () {
                  return botui.message
                    .bot({
                      loading: true,
                      delay: 1500,
                      photo: polly,
                      content:
                        "Q6. Are you able to manage your sadness, worry or tension at this moment?",
                    })
                    .then(function () {
                      return botui.action
                        .button({
                          addMessage: false,
                          action: [
                            { text: "Yes", value: 0 },
                            { text: "No", value: 1 },
                          ],
                        })
                        .then(function (res) {
                          answers[6] =
                            'Q6. Are you able to manage your sadness, worry or tension at this moment?<br/><b><font color="#FF0000">' +
                            res.text +
                            "</font></b><br/>";
                          score += res.value;
                          console.log(score);
                          return botui.message.human({
                            photo: client,
                            delay: 500,
                            content: res.text,
                          });
                        });
                    });
                });
            }
          });
      })
      .then(dispatch); //.then(confirm_answer);
  }

  function confirm_answer() {
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 2000,
        content: "Kindly confirm your answer:",
      })
      .then(function () {
        var temp = "";
        for (var i = 1; i <= 6; i++) {
          temp += "<br/>" + answers[i];
        }
        return botui.message.bot({
          loading: true,
          delay: 2000,
          photo: polly,
          content: temp,
        });
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          action: [
            { text: "Cancel (Redirect to Q1)", value: false },
            { text: "Confirm", value: true },
          ],
        });
      })
      .then(function (res) {
        if (res.value == false) {
          score = 0;
          answers = {};
          return botui.message
            .human({
              photo: client,
              delay: 500,
              content: res.text,
            })
            .then(questions);
        } else {
          return botui.message
            .human({
              photo: client,
              delay: 500,
              content: res.text,
            })
            .then(dispatch);
        }
      });
  }

  function dispatch() {
    if (score <= 6) {
      low();
    } else if (score <= 10) {
      medium();
    } else {
      high();
    }
  }

  function low() {
    return botui.message
      .bot({
        loading: true,
        delay: 3000,
        photo: polly,
        content:
          "Your answers show that you rarely or seldom encounter the feeling mentioned above, and you can manage your life well.",
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          delay: 3500,
          photo: polly,
          content:
            'Keep it up! We encourage you to take a look at the "Mental Health 101" to learn more tips for enhancing your psychological and mental wellness.',
        });
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [{ text: "Mental Health Educational Materials" }],
          })
          .then(function (res) {
            return botui.message.human({
              photo: client,
              delay: 500,
              content: res.text,
            });
          });
      })
      .then(mental_health_101);
  }

  function medium() {
    botui.message
      .bot({
        loading: true,
        delay: 1000,
        photo: polly,
        content:
          "Your answers show that you experience the feeling mentioned above quite often, and <strong>you feel your daily life get affected sometimes.</strong>",
      })
      .then(mid_recommendations);
  }

  function mid_recommendations() {
    var office_hour = isSAOWorkingHours(new Date());
    if (office_hour == true) {
      return botui.message
        .bot({
          loading: true,
          delay: 1000,
          photo: polly,
          content:
            "We recommend you to reach out our counsellors.<br/><br/>1. Making Appointment with Counsellors<br/><br/>Apart from that, you can choose other services as below:<br/><br/>2. Mental Health 101<br/>3. Immediate Contact with SAO Counsellor<br/>4. Online Chat Service<br/>5. Community Helpline",
        })
        .then(function () {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Make Appointment with SAO Counsellors", value: 3 },
                { text: "Mental Health Educational Materials", value: 1 },
                { text: "Immediate Contact with SAO Counsellors", value: 4 },
                { text: "Online Chat Service(Live)", value: 2 },
                { text: "Community Helpline", value: 6 },
              ],
            })
            .then(function (res) {
              if (res.value == 1) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(mental_health_101);
              }
              if (res.value == 2) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(T_and_C_of_OCS);
              }
              if (res.value == 3) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(make_appointment_with_counsellors);
              }
              if (res.value == 4) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(contact_with_counsellors);
              }
              if (res.value == 5) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(polyu_line);
              }
              if (res.value == 6) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(community_helpline);
              }
            });
        });
    } else {
      return botui.message
        .bot({
          loading: true,
          delay: 1000,
          photo: polly,
          content:
            "We recommend you to reach out our counsellors.<br/><br/>1. Making Appointment with SAO counsellors<br/><br/>Apart from that, you can choose other services as below:<br/><br/>2. Mental Health 101<br/>3. Immediate Contact with PolyU-Line Counsellors: (852)81001583<br/>4. Community Helpline",
        })
        .then(function () {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Make Appointment with SAO Counsellors", value: 3 },
                { text: "Mental Health Educational Materials", value: 1 },
                {
                  text: "Immediate Contact with PolyU-Line Counsellors: (852)81001583",
                  value: 5,
                },
                { text: "Community Helpline", value: 6 },
              ],
            })
            .then(function (res) {
              if (res.value == 1) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(mental_health_101);
              }
              if (res.value == 2) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(T_and_C_of_OCS);
              }
              if (res.value == 3) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(make_appointment_with_counsellors);
              }
              if (res.value == 4) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(contact_with_counsellors);
              }
              if (res.value == 5) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(polyu_line);
              }
              if (res.value == 6) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(community_helpline);
              }
            });
        });
    }
  }

  function high() {
    score = 20;
    return botui.message
      .bot({
        loading: true,
        delay: 2000,
        photo: polly,
        content:
          "Your answers show that you always experience the feeling mentioned above, and you feel your daily life always get affected.",
      })
      .then(high_recommendations);
  }

  function high_recommendations() {
    var office_hour = isSAOWorkingHours(new Date());
    if (office_hour == true) {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content:
            "Please do not hestitate to seek for professional help.<br/><br/>" +
            "<font color=blue>In case of emergency and when there is an imminent hazard posed to you and others, please call 999 or go to the nearest emergency service / A&E service.</font><br/></br>" +
            "1. Immediate Contact with SAO Counsellors<br/><br/>Apart from that, you can choose other services as below:<br/><br/>2. Making Appointment with SAO Counsellors<br/>3. Community Helpline",
        })
        .then(function () {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "Immediate Contact with SAO Counsellors", value: 4 },
              { text: "Make Appointment with SAO Counsellors", value: 3 },
              { text: "Community Helpline", value: 6 },
            ],
          });
        })
        .then(function (res) {
          if (res.value == 3) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(make_appointment_with_counsellors);
          }
          if (res.value == 4) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(contact_with_counsellors);
          }
          if (res.value == 5) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(polyu_line);
          }
          if (res.value == 6) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(community_helpline);
          }
        });
    } else {
      return botui.message
        .bot({
          loading: true,
          delay: 3000,
          photo: polly,
          content:
            "Please do not hestitate to seek for professional help.<br/><br/>" +
            "<font color=blue>In case of emergency and when there is an imminent hazard posed to you and others, please call 999 or go to the nearest emergency service / A&E service.</font><br/></br>" +
            "1. Immediate Contact with PolyU-Line Counsellors: (852)81001583<br/><br/>Apart from that, you can choose other services as below:<br/><br/>2. Making Appointment with SAO Counsellors<br/>3. Community Helpline",
        })
        .then(function () {
          return botui.action
            .button({
              addMessage: false,
              action: [
                {
                  text: "Immediately contact with PolyU-Line Counsellors",
                  value: 5,
                },
                { text: "Make Appointment with SAO Counsellors", value: 3 },
                { text: "Community Helpline", value: 6 },
              ],
            })
            .then(function (res) {
              if (res.value == 3) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(make_appointment_with_counsellors);
              }
              if (res.value == 4) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(contact_with_counsellors);
              }
              if (res.value == 5) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(polyu_line);
              }
              if (res.value == 6) {
                return botui.message
                  .human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                  })
                  .then(community_helpline);
              }
            });
        });
    }
  }

  function mental_health_101() {
    var office_hour = isSAOWorkingHours(new Date());
    return botui.message
      .bot({
        loading: true,
        delay: 1500,
        photo: polly,
        content:
          "You are being directed to a third-party website.<br/>The responsiblity of its content is subject to ownership of third-party website.",
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          delay: 2500,
          photo: polly,
          content:
            '1. <a href="http://www.google.com" target ="_blank">Academic</a><br/>'+
            '2. <a href="http://www.google.com" target ="_blank">Interpersonal Relationship</a><br/>'+
            '3. <a href="http://www.google.com" target ="_blank">Career</a><br/>'+
            '4. <a href="http://www.google.com" target ="_blank">Family</a><br/>'+
            '5. <a href="http://www.google.com" target ="_blank">Mental Health</a><br/>'+
            '6. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/courses-workshops/for-student/" target ="_blank">Psychological workshops and groups (Counselling and Wellness Section, SAO)</a><br>'+
            '7. <a href="http://www.google.com" target ="_blank">Other</a><br/>' +
            '<br><br>*In case of emergency, please Call 999 or go to the nearest emergency  / A&E service.',
        });
      })
      .then(function () {
        return botui.message.bot({
          loading: true,
          delay: 3000,
          photo: polly,
          content: "May I assist you with anything further?",
        });
      })
      .then(function () {
        return botui.action.button({
          addMessage: false,
          action: [
            { text: "No, thank you! I will stop here", value: false },
            { text: "I still need other services", value: true },
          ],
        });
      })
      .then(function (res) {
        if (res.value == false) {
          return botui.message
            .human({
              delay: 500,
              photo: client,
              content: res.text,
            })
            .then(function () {
              return botui.message.bot({
                loading: true,
                delay: 1000,
                photo: polly,
                content: "Please rate your experience",
              });
            })
            .then(end);
        } else {
          if (service_list == true) {
            botui.message.human({
                delay: 500,
                photo: client,
                content: res.text,
            }).then(init_choices);
            return;
          }
          if (office_hour == true) {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Make Appointment with SAO Counsellors", value: 1 },
                  { text: "Immediate Contact with SAO Counsellors", value: 2 },
                ],
              })
              .then(function (res) {
                if (res.value == 1) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors);
                }
                if (res.value == 2) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(contact_with_counsellors);
                }
              });
          } else {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Make Appointment with SAO Counsellors", value: 1 },
                  {
                    text: "Immediate Contact with PolyU-Line Counsellors: (852)8100-1583",
                    value: 3,
                  },
                ],
              })
              .then(function (res) {
                if (res.value == 1) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors);
                }
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(polyu_line);
                }
              });
          }
        }
      });
  }

  function T_and_C_of_OCS() {
    //Online Chat Services
    var myDate = new Date();
    pop_msg = "";

    if (myDate.getDay() >= 1 && myDate.getDay() <= 5) {
      if (myDate.getHours() >= 12 && myDate.getHours() <= 13) {
        pop_msg =
          "We'll be back in service at 1400(HKT). We look forward to meeting you !";
      } else if (myDate.getHours() == 18) {
        pop_msg =
          "We'll be back during service hours: 0900-1200 & 1400 - 1800 (HKT) , Monday through Friday. We look forward to meeting you !";
      }
    } else {
      pop_msg =
        "We'll be back at 0900(HKT) in the following working day. We look forward to meeting you !";
    }

    if (pop_msg != "") {
      botui.message
        .bot({
          loading: true,
          delay: 1500,
          photo: polly,
          content: pop_msg,
        })
        .then(end)
        .then(_close);
    }



    //----
    botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<p><b>My Polly Counselling Chatbot Service</b></p>\n" +
            "<br/>\n" +
            "<p>(The Terms and Conditions are only available in English.)</p>\n" +
            "<br/>\n" +
            "<p><b>Use of this service</b></p>\n" +
            "<p>Initiated by the SAO Counselling & Wellness Section (CWS), My Polly Counselling Chatbot Service (the “Service”) is available to all registered students of The Hong Kong Polytechnic University (the “University”) aged 18 or above.</p>\n" +
            "<br/>\n" +
            "<p>This Chatbot serves the purpose of identifying students’ service need and the referral of psychological services, ie online chat/ face-to- face counselling / online psychoeducation materials/ Non-office-hour counseling (non-crisis) / Community helplines. </p>\n",
      }).then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            {
              text: "Read more",
            },
          ],
        });
      }).then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<br/>\n" +
            "<p>The Service intends to render 'remote' support through the secured online communication. However, limitation in using the Service may exist due to a number of factors, such as technical issues (both hardware and software), instability of internet connections and lack of direct interaction. The overall service quality and user experience may thereby be affected. If possible, staff of CWS may contact with the user for the service follow-up whenever necessary. </p>\n" +
            "<br/>\n" +
            "<p>The staff of CWS will follow its protocol in providing the Service. By accepting the Service, the user of the Service shall comply with the crisis protocol suggested by the staff of CWS including calling 999, notifying police and seeking help from emergency hospital services.</p>\n",
        });
      }).then(function () {
        return botui.action.button({
          addMessage: false,
          photo: client,
          action: [
            {
              text: "Read more",
            },
          ],
        });
      }).then(function () {
        return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<br/>\n" +
            "<p>There are situations that the staff of CWS is ethically obligated to take actions to protect the user or others from harm including disclosing the personal particulars of the user of the Service to the extent necessary. These may include contacting family members, assisting hospitalization, notifying any potential victim(s) or the police. To the extent practicable, CWS will discuss with the user prior taking such actions.</p>\n" +
            "<br/>\n" +
            "<p>There will be no guarantee of any expected results or outcome from the Service. Service user shall not hold CWS responsible for the acts of the Service user. </p>\n" +
            "<br/>\n" +
            "<p>To protect the confidentiality of the service and service users, please do not make record of service in any form. </p>\n" +
            "<br/>\n" +
            '<p>You may look into the Privacy Policy Statement of PolyU <a href="https://www.polyu.edu.hk/privacy-policy-statement/" target="_blank">HERE</a>. </p>\n' +
            "<br/>\n" +
            '<p>As for the Personal Information Collection Statement, please click <a href="https://www.polyu.edu.hk/ar/web/en/pics/index.html" target="_blank">HERE</a>.</p>',
        });
      })
    //----
    /*
    botui.message
      .bot({
        loading: true,
        delay: 1000,
        photo: polly,
        content:
          "We noted that you have accepted the Terms and Conditions of using Counselling ChatBot. Before starting the Online Chat, here are a few reminders:<br/><br/>" +
          "1. In case of emergency and when " +
          "there is an imminent hazard posed to you and others, please call 999 or go to the nearest emergency / A&E service.<br/><br/>" +
          "2. Online Chat is available to all registered students of PolyU aged 18 or above.<br/><br/>" +
          "3. Please do not make record of service in any form so as to protect the confidentiality of the service and service users. <br/><br/>",
      })*/
      .then(function () {
        return botui.action.button({
          addMessage: false,
          action: [
            { text: "No, I will stop here", value: false },
            { text: "Got it", value: true },
          ],
        });
      })
      .then(function (res) {
        if (res.value == false) {
          return botui.message
            .human({
              delay: 500,
              photo: client,
              content: res.text,
            })
            .then(function () {
              return botui.message
                .bot({
                  loading: true,
                  delay: 1500,
                  photo: polly,
                  content:
                    "You are always welcome to contact us at (852)27666800 for enquires.",
                })
                .then(end);
            });
        } else {
          return botui.message
            .human({
              delay: 500,
              photo: client,
              content: res.text,
            })
            .then(questions_before_OCS);
        }
      });
  }

  function questions_before_OCS() {
    var office_hour = isSAOWorkingHours(new Date());
    return botui.message
      .bot({
        loading: true,
        delay: 1500,
        photo: polly,
        content:
          "Online Chat Service please indicate your answers(either Yes or No) below:",
      })
      .then(function () {
        return botui.message
          .bot({
            loading: true,
            delay: 1500,
            photo: polly,
            content:
              "Q1. Have you ever seen SAO counsellor(s) in the last three months or/and at present?",
          })
          .then(function () {
            return botui.action.button({
              addMessage: false,
              action: [
                { text: "Yes", value: true },
                { text: "No", value: false },
              ],
            });
          })
          .then(function (res) {
            botui.message.human({
              delay: 500,
              photo: client,
              content: res.text,
            });

            if (res.value == true) {
              return botui.message
                .bot({
                  loading: true,
                  delay: 3000,
                  photo: polly,
                  content:
                    'We encourage you to contact your existing Counsellor for counselling service directly. Please make appointment with your counsellor via phone (852)27666800, email or <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a>.',
                })
                .then(function () {
                  return botui.message.bot({
                    loading: true,
                    delay: 1500,
                    photo: polly,
                    content:
                      "Please also feel free to reach ouur online self-help materials here.",
                  });
                })
                .then(function () {
                  return botui.action.button({
                    addMessage: false,
                    action: [
                      {
                        text: "Mental Health Educational Materials",
                        value: true,
                      },
                      { text: "End of service", value: false },
                    ],
                  });
                })
                .then(function (res) {
                  if (res.value == false) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(end);
                  } else {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(mental_health_101);
                  }
                });
            } else {
              return botui.message
                .bot({
                  loading: true,
                  photo: polly,
                  delay: 3000,
                  content:
                    "Q2.Do you have a history of any of the following:<br/><br/>" +
                    "- Having thoughts of hurting yourself or others, or engaging in self-harming or violent behaviors<br/><br/>" +
                    "- Being admitted to a psychiatric ward, or hospitalized due to a psychiatric condition<br/><br/>" +
                    "- Being diagnosed of mental health problem or illness by psychologists, psychiatrists or doctors, e.g. Major Depressive Disorder, Anxiety Disorder, Schizophrenia, and any Personality Disorders etc <br/><br/>" +
                    "- Being prescribed with medications for treating a mental health related condition",
                })
                .then(function () {
                  return botui.action.button({
                    addMessage: false,
                    action: [
                      { text: "Yes", value: true },
                      { text: "No", value: false },
                    ],
                  });
                })
                .then(function (res) {
                  if (res.value == false) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(function () {
                        return botui.message.bot({
                          delay: 1000,
                          photo: polly,
                          content:
                            "Please fill in the following information prior starting a conversation with SAO counsellor",
                        });
                      })
                      .then(function () {
                        return botui.action.text({
                          addMessage: false,
                          action: {
                            size: 30,
                            placeholder: "Personal Contact Number:",
                          },
                        });
                      })
                      .then(function (res) {
                        personalInfo["contactNumber"] = res.value;
                        console.log(personalInfo);
                        return botui.message.add({
                          human: true,
                          photo: client,
                          content: "Personal contact number is " + res.value,
                        });
                      })
                      .then(function (res) {
                        return botui.action.text({
                          addMessage: false,
                          action: {
                            size: 30,
                            placeholder: "Emergency Contact Name",
                          },
                        });
                      })
                      .then(function (res) {
                        personalInfo["emergencyContactName"] = res.value;
                        console.log(personalInfo);
                        return botui.message.add({
                          human: true,
                          photo: client,
                          content: "Emergency contact name is " + res.value,
                        });
                      })
                      .then(function (res) {
                        return botui.action.text({
                          addMessage: false,
                          action: {
                            size: 30,
                            placeholder: "Relationship",
                          },
                        });
                      })
                      .then(function (res) {
                        personalInfo["relationship"] = res.value;
                        console.log(personalInfo);
                        return botui.message.add({
                          human: true,
                          photo: client,
                          content: "Relationship is " + res.value,
                        });
                      })
                      .then(function (res) {
                        return botui.action.text({
                          addMessage: false,
                          action: {
                            size: 30,
                            placeholder: "Emergency Contact Number",
                          },
                        });
                      })
                      .then(function (res) {
                        personalInfo["emergencyContactNumber"] = res.value;
                        console.log(personalInfo);
                        return botui.message.add({
                          human: true,
                          photo: client,
                          content: "Emergency contact number is " + res.value,
                        });
                      })
                      .then(function () {
                        return botui.message.bot({
                          delay: 1000,
                          photo: polly,
                          content: "Proceeding to Online Chat Service",
                        });
                      })
                      .then(function () {
                        return botui.message.add({
                          delay: 1000,
                          photo: polly,
                          content:
                            "Please wait, I am now finding a counsellor to chat with you.",
                        });
                      })
                      .then(function () {
                        return botui.message.add({
                          delay: 3000,
                          photo: polly,
                          content:
                            'For student, please click the <a target="_blank" href="http://158.132.255.165:9988/chat/student?student_netid=21&staff_netid=10">link</a> to enter the chat room.',
                        });
                      })
                      .then(function () {
                        return botui.message.add({
                          delay: 1000,
                          photo: polly,
                          content:
                            '[Demo only] For counsellor, please click the <a target="_blank" href="http://158.132.255.165:9988/chat/counsellor?student_netid=21&staff_netid=10">link</a> to enter the chat room.',
                        });
                      });
                  } else {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(function () {
                        return botui.message.bot({
                          loading: true,
                          delay: 2000,
                          photo: polly,
                          content:
                            "For facilitating the comprehensive support to you, you are highly advised to make a face to face appointment with our counsellor.",
                        });
                      })
                      .then(function () {
                        if (office_hour == true) {
                          return botui.message.bot({
                            loading: true,
                            delay: 2000,
                            photo: polly,
                            content:
                              '1. Call (852)27666800<br/>2. Walk in QT308(Entrance at Core T) during office hours<br/>3. Email: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>4. Online Booking: Direct to <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
                          });
                        } else {
                          return botui.message.bot({
                            loading: true,
                            delay: 2000,
                            photo: polly,
                            content:
                              '1. Email: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>2. Online Booking: Direct to <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
                          });
                        }
                      });
                  }
                })
                .then(end);
            }
          });
      });
  }

  function emergency_support() {
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 1500,
        content:
          '*In case of emergency, please Call 999 or go to the nearest emergency  / A&E service',
      }).then(function(){
        var office_hour = isSAOWorkingHours(new Date());
        if (office_hour == true) {
            contact_with_counsellors();
        } else {
            return botui.message.bot({
                loading: true,
                photo: polly,
                delay: 1500,
                content:
                '1. Contact with PolyU-Line Counsellors: (852)81001583 <br>' +
                '*All phone calls will be answered by Vital Employee Service Consultancy Christian Family Service Centre.<br/><br/>' +
                '2. The nearest public hospital of our campus is: Queen Elizabeth Hospital <br>' +
                '-30 Gascoigne Road, Kowloon, Hong Kong'+'<br>-Tel: (852)35068888',
            }).then(further_help);
        }
      });
  }



  function make_appointment_with_counsellors() {
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 1500,
        content:
          '1. Email: <a href="mailto:stud.counselling@polyu.edu.hk?subject=Making appointment with SAO counsellor&body=Dear Counsellor,%0D%0A%0D%0AI would like to make appointment with SAO counsellor on the following date and time:%0D%0ADate:________________%0D%0ATime: ________________%0D%0A%0D%0ALooking forward to your reply.%0D%0A%0D%0ARegards%0D%0A________________">stud.counselling@polyu.edu.hk</a><br/>2. Online Booking: <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
      })
      .then(further_help);
  }

  function contact_with_counsellors() {
    return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 1000,
          content:
            "1. Call (852)27666800<br/>2. Walk in QT308(Entrance at Core T) during office hours</br>",
      }).then(further_help());
  }

  function polyu_line() {
    return botui.message.bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content:
            "Immediate Contact with PolyU-Line Counsellors: (852)81001583<br/><br/>All phone calls will be answered by Vital Employee Service Consultancy Christian Family Service Centre.",
      }).then(further_help());
  }

  function community_helpline() {
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 3000,
        content:
          'Emergency Call: (852)999<br/>Social Welfare Department: (852)23432255<br/>Caritas Family Crisis Support Centre: (852)18288<br/>Suicide Prevention Services: (852)23820000<br/>The Samaritans Multi-lingual Suicide Prevention(852)2896-0000<br/>The Hong Kong Jockey Club Charities Trust, Open Up-24-hour online chat platform: <a href="www.openup.hk" target ="_blank">www.openup.hk</a><br/>',
      })
      .then(further_help());
  }

  function further_help() {
    return botui.message
      .bot({
        loading: true,
        photo: polly,
        delay: 3000,
        content: "May I assist you with anything further?",
      })
      .then(function () {
        return botui.action
          .button({
            addMessage: false,
            action: [
              { text: "I still need other services.", value: true },
              { text: "No, thank you! ", value: false },
            ],
          })
          .then(function (res) {
            if (res.value == true) {
              if (service_list == true) {
                botui.message.human({
                    delay: 500,
                    photo: client,
                    content: res.text,
                }).then(init_choices);
                return;
              }

              if (score <= 10) {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(mid_recommendations);
              } else {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(high_recommendations);
              }
            } else {
              return botui.message
                .human({
                  photo: client,
                  delay: 500,
                  content: res.text,
                })
                .then(function () {
                  if (score > 10) {
                    botui.message.bot({
                      loading: true,
                      photo: polly,
                      delay: 1000,
                      content: (content =
                        "<font color=blue>In case of emergency and when there is an imminent hazard posed to you and others, please call 999 or go to the nearest emergency service / A&E service.</font>"),
                    });
                  }
                })
                .then(end);
            }
          });
      });
  }

  function end() {
    rating();
  }

  function rating() {
    botui.message
      .add({
        type: "html",
        delay: 1000,
        photo: polly,
        content:
          "<p>Thank you for using our service. \n Please rate your experience now:</p >" +
          '<div class="wrap">\n' +
          '  <div class="stars">\n' +
          '    <label class="rate">\n' +
          '      <input type="radio" name="radio1" id="star1" value="star1">\n' +
          '      <i class="far fa-star star one-star available"></i>\n' +
          "    </label>\n" +
          '    <label class="rate">\n' +
          '      <input type="radio" name="radio1" id="star2" value="star2">\n' +
          '      <i class="far fa-star star two-star available"></i>\n' +
          "    </label>\n" +
          '    <label class="rate">\n' +
          '      <input type="radio" name="radio1" id="star3" value="star3">\n' +
          '      <i class="far fa-star star three-star available"></i>\n' +
          "    </label>\n" +
          '    <label class="rate">\n' +
          '      <input type="radio" name="radio1" id="star4" value="star4">\n' +
          '      <i class="far fa-star star four-star available"></i>\n' +
          "    </label>\n" +
          '    <label class="rate">\n' +
          '      <input type="radio" name="radio1" id="star5" value="star5">\n' +
          '      <i class="far fa-star star five-star available"></i>\n' +
          "    </label>\n" +
          "  </div>\n" +
          "</div>",
      })
      .then(function () {
        botui.action
          .button({
            addMessage: false,
            photo: client,
            action: [
              {
                text: "Submit my rating",
              },
            ],
          })
          .then(function () {
            // fix the stars
            console.log($(".far"));

            $(".far").removeClass("available");
            botui.message.bot({
              loading: true,
              delay: 1000,
              photo: polly,
              content: "Thank you for your valuable feedback!",
            });
          });
      })
      .then(_close);
  }

  /*
    function chatting () {
        botui.action.text({ // show 'text' action
                action: {
                    placeholder: 'Enter here'
                }
        }).then(function (res) { // get the result
            if(res.value != 'exit') {
                $(this).ajaxSubmit({
                  type: 'post',
                  url: "{% url 'auto_response' %}",
                  data:{
                      'post': res.value
                  },
                  success: function(data) {
                      response = data;
                      botui.message.add({
                        content: response
                      }).then(chatting())
                  }
                });
            } else {
                botui.message.add({
                    content: 'Bye bye!'
                });
            }
        });
    }
    */

  $(document).on(
    {
      mouseover: function (event) {
        $(this).find(".available").addClass("star-over");
        $(this).prevAll().find(".available").addClass("star-over");
      },
      mouseleave: function (event) {
        $(this).find(".available").removeClass("star-over");
        $(this).prevAll().find(".available").removeClass("star-over");
      },
    },
    ".rate"
  );

  $(document)
    .on("click", ".rate", function () {
      if (!$(this).find(".available").hasClass("rate-active")) {
        $(this)
          .siblings()
          .find(".available")
          .addClass("far")
          .removeClass("fas rate-active");
        $(this)
          .find(".available")
          .addClass("rate-active fas")
          .removeClass("far star-over");
        $(this)
          .prevAll()
          .find(".available")
          .addClass("fas")
          .removeClass("far star-over");
      } else {
        console.log("has");
      }
    })
    .on("click", ".icon-leave", function () {
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
    .on("click", ".icon-home", function () {
      location.reload();
    });
})();
