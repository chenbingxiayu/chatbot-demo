(function() {
  if ("undefined" != typeof isMainPage) {
    $("body").on("click", ".dropdown", function() {
      $(".botui-container").animate(
        { scrollTop: $(".botui-container").prop("scrollHeight") },
        1000
      );
    });

    var finish_assessment = false;
    select_language();

    function select_language() {
      return botui.message
        .bot({
          photo: polly,
          loading: true,
          searchselect: true,
          delay: 1000,
          content: "Please select your language 請選擇語言",
        })
        .then(function() {
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
            .then(function(res) {
              if (res.value == "en") {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(init_choices);
              } else if (res.value == "zh-hant") {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(init_choices_tc);
              }
            });
        });
    }

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
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Counselling ChatBOT", value: 1 },
                  {
                    text: "Mental Health Educational Materials/Resources",
                    value: 2,
                  },
                  { text: "Online Chat (Live)", value: 4 },
                  { text: "Make Appointment with SAO Counsellors", value: 5 },
                  { text: "Immediate Contact with SAO Counsellors", value: 3 },
                  { text: "Emergency Support", value: 6 },
                ],
              })
              .then(function(res) {
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
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Counselling ChatBOT", value: 1 },
                  {
                    text: "Mental Health Educational Materials/Resources",
                    value: 2,
                  },
                  { text: "Make Appointment with SAO Counsellors", value: 5 },
                  {
                    text:
                      "Immediate Contact with PolyU-Line Counsellor : (852) 8100 1583",
                    value: 3,
                  },
                  { text: "Emergency Support", value: 6 },
                ],
              })
              .then(function(res) {
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

    function get_name() {
      return botui.message
        .bot({
          photo: polly,
          loading: true,
          delay: 3000,
          content:
            'Hello! This is Polly. I\'m here to understand your service need and provide you with appropriate services.<br/><br/>You may know more about SAO services <br/><a href="https://www.polyu.edu.hk/sao/" target ="_blank">HERE</a> ',
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            photo: polly,
            delay: 1000,
            content: "May I have your name please?",
          });
        })
        .then(function() {
          return botui.action.text({
            addMessage: false,
            action: {
              size: 30,
              placeholder: "Nickname",
            },
          });
        })
        .then(function(res) {
          name = res.value;
          return botui.message.human({
            photo: client,
            delay: 500,
            content: res.value,
          });
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
        .then(function() {
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
            placeholder: "Please select your answer(s)",
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
        .then(function(res) {
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
              .then(function() {
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
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Yes", value: 1 },
                { text: "No", value: 0 },
              ],
            })
            .then(function(res) {
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
                  .then(function(res) {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          'Keep it up! We encourage you to take a look at the "Mental Health Educational Materials/Resources" to know more tips for enhancing your psychological and mental wellness.',
                      })
                      .then(mental_health_101);
                  })
                  .then(end_);
              }
              score += res.value;
              console.log(score);
              return botui.message
                .human({
                  photo: client,
                  delay: 500,
                  content: res.text,
                })
                .then(function() {
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
        .then(function() {
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
            .then(function(res) {
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
                .then(function() {
                  return botui.message
                    .bot({
                      delay: 2500,
                      loading: true,
                      photo: polly,
                      content:
                        "Awareness is the first step of change that helps to aid our self-understanding and steps of healing to take.",
                    })
                    .then(function() {
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
        .then(function() {
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
            .then(function(res) {
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
                .then(function() {
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
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Yes", value: 0 },
                { text: "No", value: 1 },
              ],
            })
            .then(function(res) {
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
                  .then(function() {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          "Q6. Do you feel effective when using these coping strategies?",
                      })
                      .then(function() {
                        return botui.action
                          .button({
                            addMessage: false,
                            action: [
                              { text: "Yes", value: 0 },
                              { text: "No", value: 1 },
                            ],
                          })
                          .then(function(res) {
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
                  .then(function() {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          "Q6. Are you able to manage your sadness, worry or tension at this moment?",
                      })
                      .then(function() {
                        return botui.action
                          .button({
                            addMessage: false,
                            action: [
                              { text: "Yes", value: 0 },
                              { text: "No", value: 1 },
                            ],
                          })
                          .then(function(res) {
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
        .then(function() {
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
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "Cancel (Redirect to Q1)", value: false },
              { text: "Confirm", value: true },
            ],
          });
        })
        .then(function(res) {
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
      finish_assessment = true;
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
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 3500,
            photo: polly,
            content:
              'Keep it up! We encourage you to take a look at the "Mental Health Educational Materials/Resources" to know more tips for enhancing your psychological and mental wellness.',
          });
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "Mental Health Educational Materials/Resources" },
              ],
            })
            .then(function(res) {
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
              "We recommend you to reach out our counsellors.<br/><br/>1. Making Appointment with Counsellors<br/><br/>Apart from that, you can choose other services as below:<br/><br/>2. Mental Health Educational Materials/Resources<br/>3. Immediate Contact with SAO Counsellor<br/>4. Online Chat Service<br/>5. Community Helpline",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Make Appointment with SAO Counsellors", value: 3 },
                  {
                    text: "Mental Health Educational Materials/Resources",
                    value: 1,
                  },
                  { text: "Immediate Contact with SAO Counsellors", value: 4 },
                  { text: "Online Chat Service(Live)", value: 2 },
                  { text: "Community Helpline", value: 6 },
                ],
              })
              .then(function(res) {
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
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "Make Appointment with SAO Counsellors", value: 3 },
                  {
                    text: "Mental Health Educational Materials/Resources",
                    value: 1,
                  },
                  {
                    text:
                      "Immediate Contact with PolyU-Line Counsellors: (852)81001583",
                    value: 5,
                  },
                  { text: "Community Helpline", value: 6 },
                ],
              })
              .then(function(res) {
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
          .then(function() {
            return botui.action.button({
              addMessage: false,
              action: [
                { text: "Immediate Contact with SAO Counsellors", value: 4 },
                { text: "Make Appointment with SAO Counsellors", value: 3 },
                { text: "Community Helpline", value: 6 },
              ],
            });
          })
          .then(function(res) {
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
          .then(function() {
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
              .then(function(res) {
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

    // **************************

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
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 2500,
            photo: polly,
            content:
              '1. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/academic/" target ="_blank">Academic</a><br/>' +
              '2. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/interpersonal-relationship/" target ="_blank">Interpersonal Relationship</a><br/>' +
              '3. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/career/" target ="_blank">Career</a><br/>' +
              '4. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/family/" target ="_blank">Family</a><br/>' +
              '5. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/mental-health/" target ="_blank">Mental Health</a><br/>' +
              '6. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/courses-workshops/for-student/" target ="_blank">CWS Psychological workshops and groups</a><br>' +
              '7. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/others/" target ="_blank">Others</a><br/>' +
              "<br><br>*In case of emergency, please call 999 or go to the nearest emergency  / A&E service.",
          });
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 3000,
            photo: polly,
            content:
              "Thank you for using our service. May I assist you with anything further?",
          });
        })
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "No, thank you! I will stop here", value: false },
              { text: "I still need other services", value: true },
            ],
          });
        })
        .then(function(res) {
          if (res.value == false) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(function() {
                return botui.message.bot({
                  loading: true,
                  delay: 1000,
                  photo: polly,
                  content: "Please rate your experience",
                });
              })
              .then(end);
          } else {
            if (service_list == true || finish_assessment == false) {
              botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(init_choices);
              return;
            }
            if (office_hour == true) {
              return botui.action
                .button({
                  addMessage: false,
                  action: [
                    { text: "Make Appointment with SAO Counsellors", value: 1 },
                    {
                      text: "Immediate Contact with SAO Counsellors",
                      value: 2,
                    },
                  ],
                })
                .then(function(res) {
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
                      text:
                        "Immediate Contact with PolyU-Line Counsellors: (852)8100-1583",
                      value: 3,
                    },
                  ],
                })
                .then(function(res) {
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
      // return Promise.resolve().then(questions_before_OCS);
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

      // pop_msg = "";

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
      botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<p>Please accept the Terms and Conditions of using the Online Chat service:</p><br/>" +
            "<p>(The Terms and Conditions are only available in English.)</p>\n" +
            "<br/>\n" +
            "<p>Initiated by the SAO Counselling & Wellness Section (CWS), Online Chat Service (the Service) is available to all registered students of The Hong Kong Polytechnic University (PolyU) aged 18 or above.</p>\n",
        })
        .then(function() {
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
        .then(function() {
          return botui.message.bot({
            loading: true,
            photo: polly,
            delay: 2000,
            content:
              "<br/>\n" +
              "<p>The Service intends to render remote support through the secured online communication.  However, limitation in using the Service may exist due to a number of factors, such as technical issues (both hardware and software), instability of internet connections and lack of direct interaction. The overall service quality and user experience may thereby be affected.  If possible, staff of CWS may contact the user for the service follow-up whenever necessary.  </p>\n" +
              "<br/>\n" +
              "<p>The staff of CWS will follow its protocol in providing the Service.  By accepting the Service, the user of the Service shall comply with the crisis protocol suggested by the staff of CWS including calling 999, notifying police and seeking help from emergency hospital services.</p>\n",
          });
        })
        .then(function() {
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
        .then(function() {
          return botui.message.bot({
            loading: true,
            photo: polly,
            delay: 2000,
            content:
              "<br/>\n" +
              "<p>There are situations that the staff of CWS is ethically obligated to take actions to protect the user of the Service or others from harm including disclosing the personal particulars of the user to the extent necessary. These may include contacting family members, assisting hospitalization, notifying any potential victim(s) or the police.   To the extent practicable, counsellor of CWS will discuss with the user prior taking such actions.</p>\n" +
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
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "No, I will stop here", value: false },
              { text: "Got it", value: true },
            ],
          });
        })
        .then(function(res) {
          if (res.value == false) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(function() {
                return botui.message
                  .bot({
                    loading: true,
                    delay: 1500,
                    photo: polly,
                    content:
                      "You are always welcome to contact us at (852)27666800 for enquires.",
                  })
                  .then(further_help);
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
          content: "Please indicate your answers (either Yes or No) below:",
        })
        .then(function() {
          return botui.message
            .bot({
              loading: true,
              delay: 1500,
              photo: polly,
              content:
                "Q1. Have you ever received counselling from SAO counsellor(s) in the last three months and/or at present?",
            })
            .then(function() {
              return botui.action.button({
                addMessage: false,
                action: [
                  { text: "Yes", value: true },
                  { text: "No", value: false },
                ],
              });
            })
            .then(function(res) {
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
                  .then(function() {
                    return botui.message.bot({
                      loading: true,
                      delay: 1500,
                      photo: polly,
                      content:
                        "You are always welcome to read our online self-help materials here.",
                    });
                  })
                  .then(function() {
                    return botui.action.button({
                      addMessage: false,
                      action: [
                        {
                          text: "Mental Health Educational Materials/Resources",
                          value: true,
                        },
                        { text: "No, thank you!", value: false },
                      ],
                    });
                  })
                  .then(function(res) {
                    if (res.value == false) {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(further_help);
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
                  .then(function() {
                    return botui.action.button({
                      addMessage: false,
                      action: [
                        { text: "Yes", value: true },
                        { text: "No", value: false },
                      ],
                    });
                  })
                  .then(function(res) {
                    if (res.value == false) {
                      // TODO student id
                      const student_netid = "TEST_STUDENT_ID".toLocaleUpperCase();
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(function() {
                          return botui.message.bot({
                            delay: 1000,
                            photo: polly,
                            content:
                              "Please fill in the following information prior starting a conversation with SAO counsellor",
                          });
                        })
                        .then(function() {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "Personal Contact Number:",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["contactNumber"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "Personal contact number is " + res.value,
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "Emergency Contact Name",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["emergencyContactName"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "Emergency contact name is " + res.value,
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "Relationship",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["relationship"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "Relationship is " + res.value,
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "Emergency Contact Number",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["emergencyContactNumber"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "Emergency contact number is " + res.value,
                          });
                        })
                        .then(function() {
                          return botui.message.bot({
                            delay: 1000,
                            photo: polly,
                            content: "Proceeding to Online Chat Service",
                          });
                        })
                        .then(async function() {
                          const responseMessage = await addToQueue(
                            student_netid
                          );
                          const isAssigned =
                            responseMessage.indexOf(
                              "Student is assigned to a staff"
                            ) > -1;

                          if (isAssigned) {
                            return Promise.resolve("assigned");
                          } else {
                            await botui.message.add({
                              delay: 1000,
                              photo: polly,
                              content:
                                "Please wait, I am now finding a counsellor to chat with you.",
                            });

                            return Promise.resolve("waiting");
                          }
                        })
                        .then(async function(status) {
                          let currentStatus = status;
                          if (currentStatus == "waiting") {
                            while (true) {
                              // request after 2 mins(120000 = 2 * 60 * 1000)
                              await new Promise((resolve) =>
                                setTimeout(resolve, 120000)
                              );

                              const stu = await getStatusByStudentNetId(
                                student_netid
                              );

                              if (stu.student_chat_status === "waiting") {
                                const queueList = await getQueueStatus(
                                  student_netid
                                );

                                const waitingNo = queueList.findIndex(
                                  (student) =>
                                    student.fields.student_netid ==
                                    student_netid
                                );
                                await waitSubsribe(student_netid, waitingNo);
                              } else {
                                // assign or end
                                currentStatus = stu.student_chat_status;
                                break;
                              }
                            }
                          }

                          if (currentStatus.toLocaleLowerCase() === "end") {
                            throw new Error(
                              "Thank you for using our service, you may make an appointment with our counsellor via POSS or call 2766 6800 if needed."
                            );
                          }

                          if (
                            currentStatus.toLocaleLowerCase() === "assigned"
                          ) {
                            while (true) {
                              const stu = await getStatusByStudentNetId(
                                student_netid
                              );
                              if (stu.student_chat_status === "chatting") {
                                await botui.message.add({
                                  delay: 1000,
                                  photo: polly,
                                  content: `please click the <a target="_blank" href="/main/chat/student/?student_netid=${student_netid}&staff_netid=${stu.assigned_counsellor}">link</a> to enter the chat room.`,
                                });
                                break;
                              } else {
                                await botui.message.add({
                                  delay: 1000,
                                  photo: polly,
                                  content:
                                    "You have been assigned to a counsellor, please wait.",
                                });
                                // request after 2 mins(120000 = 2 * 60 * 1000)
                                await new Promise((resolve) =>
                                  setTimeout(resolve, 120000)
                                );
                              }
                            }
                          }
                        })
                        .catch(function(e) {
                          return botui.message.add({
                            delay: 1000,
                            photo: polly,
                            content: e.message,
                          });
                        });
                      // .then(function () {
                      //   return botui.message.add({
                      //     delay: 1000,
                      //     photo: polly,
                      //     content:
                      //       '[Demo only] For counsellor, please click the <a target="_blank" href="http://158.132.255.165:9988/chat/counsellor?student_netid=21&staff_netid=10">link</a> to enter the chat room.',
                      //   });
                      // });
                    } else {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(function() {
                          return botui.message.bot({
                            loading: true,
                            delay: 2000,
                            photo: polly,
                            content:
                              "To provide comprehensive support to you, you are highly advised to make a face to face appointment with SAO counsellor.",
                          });
                        })
                        .then(function() {
                          if (office_hour == true) {
                            return botui.message.bot({
                              loading: true,
                              delay: 1000,
                              photo: polly,
                              content:
                                '1. Call (852)27666800<br/>2. Walk in QT308(Entrance at Core T) during office hours<br/>3. Email: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>4. Online Booking: <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
                            });
                          } else {
                            return botui.message.bot({
                              loading: true,
                              delay: 2000,
                              photo: polly,
                              content:
                                '1. Email: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>2. Online Booking: <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
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
            "<font color=black>In case of emergency, please Call 999 or go to the nearest emergency  / A&E service.</font>",
        })
        .then(function() {
          var office_hour = isSAOWorkingHours(new Date());
          if (office_hour == true) {
            contact_with_counsellors();
          } else {
            return botui.message
              .bot({
                loading: true,
                photo: polly,
                delay: 1500,
                content:
                  "1. Contact with PolyU-Line Counsellors: (852)81001583 <br>" +
                  "*All phone calls will be answered by Vital Employee Service Consultancy Christian Family Service Centre.<br/><br/>" +
                  "2. The nearest public hospital of our campus is: Queen Elizabeth Hospital <br>" +
                  "-30 Gascoigne Road, Kowloon, Hong Kong" +
                  "<br>-Tel: (852)35068888",
              })
              .then(further_help);
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
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 100,
          content:
            "1. Call (852)27666800<br/>2. Walk in QT308(Entrance at Core T) during office hours</br>",
        })
        .then(further_help());
    }

    function polyu_line() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content:
            "Immediate Contact with PolyU-Line Counsellors: (852)81001583<br/><br/>All phone calls will be answered by Vital Employee Service Consultancy Christian Family Service Centre.",
        })
        .then(further_help());
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
          content:
            "Thank you for using our service. May I assist you with anything further?",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "I still need other services.", value: true },
                { text: "No, thank you! ", value: false },
              ],
            })
            .then(function(res) {
              if (res.value == true) {
                if (service_list == true || finish_assessment == false) {
                  botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(init_choices);
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
                  .then(function() {
                    if (score > 10 || service_list == true) {
                      botui.message.bot({
                        loading: true,
                        photo: polly,
                        delay: 1000,
                        content: (content =
                          "<font color=black>In case of emergency, please call 999 or go to the nearest emergency  / A&E service.</font>"),
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
            "<p>Please rate your experience now:</p >" +
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
        .then(function() {
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
            .then(function() {
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
        mouseover: function(event) {
          $(this)
            .find(".available")
            .addClass("star-over");
          $(this)
            .prevAll()
            .find(".available")
            .addClass("star-over");
        },
        mouseleave: function(event) {
          $(this)
            .find(".available")
            .removeClass("star-over");
          $(this)
            .prevAll()
            .find(".available")
            .removeClass("star-over");
        },
      },
      ".rate"
    );

    $(document)
      .on("click", ".rate", function() {
        if (
          !$(this)
            .find(".available")
            .hasClass("rate-active")
        ) {
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

    // Traditional chinese

    function init_choices_tc() {
      var office_hour = isSAOWorkingHours(new Date());
      if (office_hour == true) {
        return botui.message
          .bot({
            loading: true,
            delay: 1000,
            photo: polly,
            content: "請選擇以下服務:",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "網上聊天機械人", value: 1 },
                  { text: "心理健康教育資訊/資源", value: 2 },
                  { text: "線上聊天", value: 4 },
                  { text: "預約輔導服務", value: 5 },
                  { text: "立即與學生事務處 (SAO)輔導員聯絡", value: 3 },
                  { text: "緊急支援", value: 6 },
                ],
              })
              .then(function(res) {
                if (res.value == 1) {
                  service_list = false;
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(get_name_tc)
                    .then(questions_tc);
                }
                if (res.value == 2) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(mental_health_101_tc);
                }
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(contact_with_counsellors_tc);
                }
                if (res.value == 4) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(T_and_C_of_OCS_tc);
                }
                if (res.value == 5) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors_tc);
                }
                if (res.value == 6) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(emergency_support_tc);
                }
              });
          });
      } else {
        return botui.message
          .bot({
            loading: true,
            delay: 1000,
            photo: polly,
            content: "請選擇以下服務:",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "網上聊天機械人", value: 1 },
                  { text: "心理健康教育資訊/資源", value: 2 },
                  { text: "預約輔導服務", value: 5 },
                  {
                    text: "立即與PolyU-Line輔導員聯絡 : (852) 8100 1583",
                    value: 3,
                  },
                  { text: "緊急支援", value: 6 },
                ],
              })
              .then(function(res) {
                if (res.value == 1) {
                  service_list = false;
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(get_name_tc)
                    .then(questions_tc);
                }
                if (res.value == 2) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(mental_health_101_tc);
                }
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(polyu_line_tc);
                }
                if (res.value == 5) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors_tc);
                }
                if (res.value == 6) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(emergency_support_tc);
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

    function get_name_tc() {
      return botui.message
        .bot({
          photo: polly,
          loading: true,
          delay: 3000,
          content:
            '你好，我是Polly。我會根據你以下所提供的訊息，為你建議合適的服務。<br/><br/>如欲查詢有關學生事務處的其他服務，請參閱以下連結 <br/><a href="https://www.polyu.edu.hk/sao/" target ="_blank">HERE</a> ',
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            photo: polly,
            delay: 1000,
            content: "你的名字是?",
          });
        })
        .then(function() {
          return botui.action.text({
            addMessage: false,
            action: {
              size: 30,
              placeholder: "輸入名字",
            },
          });
        })
        .then(function(res) {
          name = res.value;
          return botui.message.human({
            photo: client,
            delay: 500,
            content: res.value,
          });
        });
    }

    function questions_tc() {
      botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 1500,
          content:
            "你好﹗" +
            name +
            "，請回答以下問題，我會總結所得出的答案，提出切合你所需的服務建議。<br/><br/> 以下提問並不能視之為取代專業臨床的心理評估和診斷",
        })
        .then(function() {
          botui.message
            .bot({
              loading: true,
              delay: 1500,
              photo: polly,
              content: "Q1. 你此刻想傾談的內容是？ (可選一或多項)",
            })
            .then(q1_ans_tc);
        });
    }

    function q1_ans_tc() {
      $(".botui-container").animate(
        { scrollTop: $(".botui-container").prop("scrollHeight") },
        1000
      );
      return botui.action
        .select({
          addMessage: false,
          action: {
            placeholder: "請選擇",
            multipleselect: true,
            options: [
              { text: "學業" },
              { text: "人際關係" },
              { text: "工作" },
              { text: "家庭" },
              { text: "精神健康" },
              { text: "其他" },
            ],
            button: {
              icon: "check",
              label: "OK",
            },
          },
        })
        .then(function(res) {
          if (res.text == "") {
            alert("您必須至少選擇一項！");
            q1_ans();
          } else {
            answers[1] =
              'Q1. 你此刻想傾談的內容是？ (可選一或多項)<br/><b><font color="#FF0000">' +
              res.text +
              "</font></b><br/>";
            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(function() {
                return botui.message.bot({
                  loading: true,
                  delay: 1000,
                  photo: polly,
                  content: "好的，你現正面對有關" + res.text + "的事情。",
                });
              })
              .then(q2_tc);
          }
        });
    }

    function q2_tc() {
      botui.message
        .bot({
          loading: true,
          delay: 1500,
          photo: polly,
          content: "Q2. 面對以上的事情，你有沒有感到不愉快、擔心或緊張？",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "有", value: 1 },
                { text: "沒有", value: 0 },
              ],
            })
            .then(function(res) {
              answers[2] =
                'Q2. 面對以上的事情，你有沒有感到不愉快、擔心或緊張？<br/><b><font color="#FF0000">' +
                res.text +
                "</font></b><br/>";
              if (res.value == 0) {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(function(res) {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          "我建議你可以參閱心理健康教育資訊/資源，獲取更多提升心理健康的小貼士。",
                      })
                      .then(mental_health_101_tc);
                  })
                  .then(end__tc);
              }
              score += res.value;
              console.log(score);
              return botui.message
                .human({
                  photo: client,
                  delay: 500,
                  content: res.text,
                })
                .then(function() {
                  return botui.message.bot({
                    loading: true,
                    delay: 1500,
                    photo: polly,
                    content:
                      "感謝你讓我知道。我們在日常生活中經驗這些感覺是很自然的事。",
                  });
                });
            });
        })
        .then(q3_tc);
    }

    function q3_tc() {
      botui.message
        .bot({
          loading: true,
          delay: 1500,
          photo: polly,
          content: "Q3. 你有多經常因為上述的事情而感到不愉快、擔心或緊張？",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "極少", value: 1 },
                { text: "頗少", value: 2 },
                { text: "一般", value: 3 },
                { text: "頗多", value: 4 },
                { text: "極多", value: 5 },
              ],
            })
            .then(function(res) {
              answers[3] =
                'Q3. 你有多經常因為上述的事情而感到不愉快、擔心或緊張？<br/><b><font color="#FF0000">' +
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
                .then(function() {
                  return botui.message
                    .bot({
                      delay: 2500,
                      loading: true,
                      photo: polly,
                      content:
                        "覺察是改變的第一步，能夠提升自我了解及促進復原。",
                    })
                    .then(function() {
                      return botui.message.bot({
                        delay: 1000,
                        loading: true,
                        photo: polly,
                        content: "我看得出你能夠覺察到自己正受不同的情緒困擾。",
                      });
                    });
                });
            });
        })
        .then(q4_tc);
    }

    function q4_tc() {
      botui.message
        .bot({
          loading: true,
          delay: 2000,
          photo: polly,
          content: "Q4. 這些情緒有多經常影響你的日常生活？",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "極少", value: 1 },
                { text: "頗少", value: 2 },
                { text: "一般", value: 3 },
                { text: "頗多", value: 4 },
                { text: "極多", value: 5 },
              ],
            })
            .then(function(res) {
              answers[4] =
                'Q4. 這些情緒有多經常影響你的日常生活？<br/><b><font color="#FF0000">' +
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
                .then(function() {
                  return botui.message.bot({
                    loading: true,
                    photo: polly,
                    delay: 1500,
                    content: "我明白這些情緒正在影響著你的日常生活。",
                  });
                });
            });
        })
        .then(q5_q6_tc);
    }

    function q5_q6_tc() {
      botui.message
        .bot({
          loading: true,
          delay: 2500,
          photo: polly,
          content:
            "Q5. 你曾否採用一些積極的應對方法 (例如: 運動、呼吸練習、聽音樂等）去面對/紓緩這些情緒嗎?",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "有", value: 0 },
                { text: "沒有", value: 1 },
              ],
            })
            .then(function(res) {
              answers[5] =
                'Q5. 你曾否採用一些積極的應對方法 (例如: 運動、呼吸練習、聽音樂等）去面對/紓緩這些情緒嗎?<br/><b><font color="#FF0000">' +
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
                      "我們能發掘一些積極的應對方法去紓緩上述的情緒是非常重要的啊!",
                  })
                  .then(function() {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          "Q6. 你認為這些應對方法能否有效紓緩你上述的情緒嗎?",
                      })
                      .then(function() {
                        return botui.action
                          .button({
                            addMessage: false,
                            action: [
                              { text: "能夠", value: 0 },
                              { text: "不能夠", value: 1 },
                            ],
                          })
                          .then(function(res) {
                            answers[6] =
                              'Q6. 你認為這些應對方法能否有效紓緩你上述的情緒嗎?<br/><b><font color="#FF0000">' +
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
                      "我們能發掘一些積極的應對方法去紓緩上述的情緒是非常重要的啊!",
                  })
                  .then(function() {
                    return botui.message
                      .bot({
                        loading: true,
                        delay: 1500,
                        photo: polly,
                        content:
                          "Q6. 此刻，你認為你有能力有效地紓緩上述情緒嗎？",
                      })
                      .then(function() {
                        return botui.action
                          .button({
                            addMessage: false,
                            action: [
                              { text: "能夠", value: 0 },
                              { text: "不能夠", value: 1 },
                            ],
                          })
                          .then(function(res) {
                            answers[6] =
                              'Q6. 此刻，你認為你有能力有效地紓緩上述情緒嗎？<br/><b><font color="#FF0000">' +
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
        .then(dispatch_tc); //.then(confirm_answer);
    }

    function confirm_answer_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content: "請確認您的回答:",
        })
        .then(function() {
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
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "取消（重定向到 Q1）", value: false },
              { text: "確認", value: true },
            ],
          });
        })
        .then(function(res) {
          if (res.value == false) {
            score = 0;
            answers = {};
            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(questions_tc);
          } else {
            return botui.message
              .human({
                photo: client,
                delay: 500,
                content: res.text,
              })
              .then(dispatch_tc);
          }
        });
    }

    function dispatch_tc() {
      finish_assessment = true;
      if (score <= 6) {
        low_tc();
      } else if (score <= 10) {
        medium_tc();
      } else {
        high_tc();
      }
    }

    function low_tc() {
      return botui.message
        .bot({
          loading: true,
          delay: 3000,
          photo: polly,
          content:
            "你所選擇的答案顯示你當下鮮有或甚少經歷上述的情緒狀況，並能有效地管理情緒。",
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 3500,
            photo: polly,
            content:
              "做得好﹗請繼續保持心理健康！我建議你可以參閱心理健康教育資訊/資源，獲取更多提升心理健康的小貼士。",
          });
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [{ text: "心理健康教育資訊/資源" }],
            })
            .then(function(res) {
              return botui.message.human({
                photo: client,
                delay: 500,
                content: res.text,
              });
            });
        })
        .then(mental_health_101_tc);
    }

    function medium_tc() {
      botui.message
        .bot({
          loading: true,
          delay: 1000,
          photo: polly,
          content:
            "你所選擇的答案顯示你有時候會經歷上述的情緒，而這些情緒狀況<strong>有時侯會影響到你的日常生活。</strong>",
        })
        .then(mid_recommendations_tc);
    }

    function mid_recommendations_tc() {
      var office_hour = isSAOWorkingHours(new Date());
      if (office_hour == true) {
        return botui.message
          .bot({
            loading: true,
            delay: 1000,
            photo: polly,
            content:
              "我們建議你與學生事務處(SAO)的輔導員聯絡。<br/><br/>1. 預約輔導服務<br/><br/>除此之外，您還可以選擇以下服務：<br/><br/>2. 心理健康教育資訊/資源<br/>3. 立即與學生事務處 (SAO)輔導員聯絡<br/>4. 線上聊天室<br/>5. 社區支援熱線",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "預約輔導服務", value: 3 },
                  { text: "心理健康教育資訊/資源", value: 1 },
                  { text: "立即與SAO 輔導員聯絡", value: 4 },
                  { text: "線上聊天", value: 2 },
                  { text: "社區支援熱線", value: 6 },
                ],
              })
              .then(function(res) {
                if (res.value == 1) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(mental_health_101_tc);
                }
                if (res.value == 2) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(T_and_C_of_OCS_tc);
                }
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors_tc);
                }
                if (res.value == 4) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(contact_with_counsellors_tc);
                }
                if (res.value == 5) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(polyu_line_tc);
                }
                if (res.value == 6) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(community_helpline_tc);
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
              "我們建議你與學生事務處(SAO)的輔導員聯絡。<br/><br/>1. 預約輔導服務<br/><br/>除此之外，您還可以選擇以下服務：<br/><br/>2. 心理健康教育資訊/資源<br/>3. 立即與PolyU-Line輔導員聯絡 : (852) 81001583<br/>4. 社區支援熱線",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  { text: "預約輔導服務", value: 3 },
                  { text: "心理健康教育資訊/資源", value: 1 },
                  {
                    text: "立即與PolyU-Line輔導員聯絡 : (852) 8100 1583",
                    value: 5,
                  },
                  { text: "社區支援熱線", value: 6 },
                ],
              })
              .then(function(res) {
                if (res.value == 1) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(mental_health_101_tc);
                }
                if (res.value == 2) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(T_and_C_of_OCS_tc);
                }
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors_tc);
                }
                if (res.value == 4) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(contact_with_counsellors_tc);
                }
                if (res.value == 5) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(polyu_line_tc);
                }
                if (res.value == 6) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(community_helpline_tc);
                }
              });
          });
      }
    }

    function high_tc() {
      score = 20;
      return botui.message
        .bot({
          loading: true,
          delay: 2000,
          photo: polly,
          content:
            "你所選擇的答案顯示你當下經常會經歷到上述的情緒，而這些情緒狀況亦不時影響著你的日常生活。",
        })
        .then(high_recommendations_tc);
    }

    function high_recommendations_tc() {
      var office_hour = isSAOWorkingHours(new Date());
      if (office_hour == true) {
        return botui.message
          .bot({
            loading: true,
            photo: polly,
            delay: 3000,
            content:
              "我們建議你儘快向專業人士尋求協助。<br/><br/>" +
              "<font color=blue>如果你正身處緊急情況或/及險境，並有感自身及/或他人有即時的生命危險，請即致電999或到鄰近的急症室求助。</font><br/></br>" +
              "1. 立即與學生事務處 (SAO)輔導員聯絡<br/><br/>除此之外，您還可以選擇以下服務：<br/><br/>2. 預約輔導服務<br/>3. 社區支援熱線",
          })
          .then(function() {
            return botui.action.button({
              addMessage: false,
              action: [
                { text: "立即與SAO 輔導員聯絡", value: 4 },
                { text: "預約輔導服務", value: 3 },
                { text: "社區支援熱線", value: 6 },
              ],
            });
          })
          .then(function(res) {
            if (res.value == 3) {
              return botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(make_appointment_with_counsellors_tc);
            }
            if (res.value == 4) {
              return botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(contact_with_counsellors_tc);
            }
            if (res.value == 5) {
              return botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(polyu_line_tc);
            }
            if (res.value == 6) {
              return botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(community_helpline_tc);
            }
          });
      } else {
        return botui.message
          .bot({
            loading: true,
            delay: 3000,
            photo: polly,
            content:
              "我們建議你儘快向專業人士尋求協助。<br/><br/>" +
              "<font color=blue>如果你正身處緊急情況或/及險境，並有感自身及/或他人有即時的生命危險，請即致電999或到鄰近的急症室求助。</font><br/></br>" +
              "1. 立即與PolyU-Line輔導員聯絡 : (852) 81001583<br/><br/>除此之外，您還可以選擇以下服務：<br/><br/>2. 預約輔導服務<br/>3. 社區支援熱線",
          })
          .then(function() {
            return botui.action
              .button({
                addMessage: false,
                action: [
                  {
                    text: "立即與PolyU-Line輔導員聯絡 : (852) 8100 1583",
                    value: 5,
                  },
                  { text: "立即與SAO 輔導員聯絡", value: 3 },
                  { text: "社區支援熱線", value: 6 },
                ],
              })
              .then(function(res) {
                if (res.value == 3) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(make_appointment_with_counsellors_tc);
                }
                if (res.value == 4) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(contact_with_counsellors_tc);
                }
                if (res.value == 5) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(polyu_line_tc);
                }
                if (res.value == 6) {
                  return botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(community_helpline_tc);
                }
              });
          });
      }
    }

    function mental_health_101_tc() {
      var office_hour = isSAOWorkingHours(new Date());
      return botui.message
        .bot({
          loading: true,
          delay: 1500,
          photo: polly,
          content:
            "以下連結將轉接至第三方網站。有關第三方網站的內容，我們概不負責，請參閱該網站的條款和政策。",
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 2500,
            photo: polly,
            content:
              '1. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/academic/" target ="_blank">學業</a><br/>' +
              '2. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/interpersonal-relationship/" target ="_blank">人際關係</a><br/>' +
              '3. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/career/" target ="_blank">工作</a><br/>' +
              '4. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/family/" target ="_blank">家庭</a><br/>' +
              '5. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/mental-health/" target ="_blank">精神健康</a><br/>' +
              '6. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/courses-workshops/for-student/" target ="_blank">CWS心理健康小組及工作坊</a><br>' +
              '7. <a href="https://www.polyu.edu.hk/sao/cws/student-counselling/mental-health-educational-material-resources/others/" target ="_blank">其他</a><br/>' +
              "<br><br>*如果你正身處緊急情況及/或險境，並有感自身及/或他人有即時的生命危險，請即致電999或到鄰近的急症室求助。", //? In case of emergency, please call 999 or go to the nearest emergency / A&E service.
          });
        })
        .then(function() {
          return botui.message.bot({
            loading: true,
            delay: 3000,
            photo: polly,
            content: "多謝你使用我們的服務。請問你還有其他需要嗎？",
          });
        })
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "不需要了，謝謝。", value: false },
              { text: "我仍需要其他服務。", value: true },
            ],
          });
        })
        .then(function(res) {
          if (res.value == false) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(function() {
                return botui.message.bot({
                  loading: true,
                  delay: 1000,
                  photo: polly,
                  content: "請分享你對本服務的體驗",
                });
              })
              .then(end_tc);
          } else {
            if (service_list == true || finish_assessment == false) {
              botui.message
                .human({
                  delay: 500,
                  photo: client,
                  content: res.text,
                })
                .then(init_choices_tc);
              return;
            }
            if (office_hour == true) {
              return botui.action
                .button({
                  addMessage: false,
                  action: [
                    { text: "預約輔導服務", value: 1 },
                    { text: "立即與學生事務處(SAO)輔導員聯絡", value: 2 },
                  ],
                })
                .then(function(res) {
                  if (res.value == 1) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(make_appointment_with_counsellors_tc);
                  }
                  if (res.value == 2) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(contact_with_counsellors_tc);
                  }
                });
            } else {
              return botui.action
                .button({
                  addMessage: false,
                  action: [
                    { text: "預約輔導服務", value: 1 },
                    {
                      text: "立即與PolyU-Line輔導員聯絡: (852)8100-1583",
                      value: 3,
                    },
                  ],
                })
                .then(function(res) {
                  if (res.value == 1) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(make_appointment_with_counsellors_tc);
                  }
                  if (res.value == 3) {
                    return botui.message
                      .human({
                        delay: 500,
                        photo: client,
                        content: res.text,
                      })
                      .then(polyu_line_tc);
                  }
                });
            }
          }
        });
    }

    function T_and_C_of_OCS_tc() {
      //Online Chat Services
      var myDate = new Date();
      pop_msg = "";

      if (myDate.getDay() >= 1 && myDate.getDay() <= 5) {
        if (myDate.getHours() >= 12 && myDate.getHours() <= 13) {
          pop_msg =
            "我們會在下午二時(香港時間)提供服務，期待屆時與你在線上聊天。";
        } else if (myDate.getHours() == 18) {
          pop_msg =
            "我們會在星期一至星期五，上午9時至中午12時(香港時間)和下午2時至下午6時(香港時間)提供服務，期待屆時與你在線上聊天。";
        }
      } else {
        pop_msg =
          "我們會在下一個工作天的上午9時(香港時間)提供服務，期待屆時與你在線上聊天。";
      }

      if (pop_msg != "") {
        botui.message
          .bot({
            loading: true,
            delay: 1500,
            photo: polly,
            content: pop_msg,
          })
          .then(end_tc)
          .then(_close);
      }

      //----
      botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 2000,
          content:
            "<p>請閱讀以下服務條款及私隱政策:</p><br/>" + //? Please accept the Terms and Conditions of using the Online Chat service
            "<p><b>My Polly Counselling Chatbot Service</b></p>\n" +
            "<br/>\n" +
            "<p>(The Terms and Conditions are only available in English.)</p>\n" +
            "<br/>\n" +
            "<p>Initiated by the SAO Counselling & Wellness Section (CWS), My Polly Counselling Chatbot Service (the “Service”) is available to all registered students of The Hong Kong Polytechnic University (the “University”) aged 18 or above.</p>\n" +
            "<br/>\n" +
            "<p>This Chatbot serves the purpose of identifying students’ service need and the referral of psychological services, ie online chat/face-to-face counselling / online psychoeducation materials/ Non-office-hour counseling (non-crisis) / Community helplines. </p>\n",
        })
        .then(function() {
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
        .then(function() {
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
        .then(function() {
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
        .then(function() {
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
        .then(function() {
          return botui.action.button({
            addMessage: false,
            action: [
              { text: "不需要了，謝謝。", value: false },
              { text: "同意", value: true },
            ],
          });
        })
        .then(function(res) {
          if (res.value == false) {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(function() {
                return botui.message
                  .bot({
                    loading: true,
                    delay: 1500,
                    photo: polly,
                    content:
                      "如有需要，歡迎你致電 (852)27666800 與SAO輔導員聯絡。",
                  })
                  .then(further_help_tc);
              });
          } else {
            return botui.message
              .human({
                delay: 500,
                photo: client,
                content: res.text,
              })
              .then(questions_before_OCS_tc);
          }
        });
    }

    function questions_before_OCS_tc() {
      var office_hour = isSAOWorkingHours(new Date());
      return botui.message
        .bot({
          loading: true,
          delay: 1500,
          photo: polly,
          content: "請回答以下問題，並選擇「是」或「否」作答：",
        })
        .then(function() {
          return botui.message
            .bot({
              loading: true,
              delay: 1500,
              photo: polly,
              content:
                "Q1. 在過去的三個月或至現在，你曾否或正接受身心健康及輔導部的輔導服務嗎?",
            })
            .then(function() {
              return botui.action.button({
                addMessage: false,
                action: [
                  { text: "有", value: true },
                  { text: "沒有", value: false },
                ],
              });
            })
            .then(function(res) {
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
                      '我們鼓勵你與正跟進你的SAO輔導員直接聯絡。你可以致電(852)27666800、透過電郵或網上系統<a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a>與你的輔導員預約面談時間。',
                  })
                  .then(function() {
                    return botui.message.bot({
                      loading: true,
                      delay: 1500,
                      photo: polly,
                      content: "與此同時，歡迎瀏覽我們的心理健康教育資訊。",
                    });
                  })
                  .then(function() {
                    return botui.action.button({
                      addMessage: false,
                      action: [
                        {
                          text: "心理健康教育資訊/資源",
                          value: true,
                        },
                        { text: "不需要了，謝謝。", value: false },
                      ],
                    });
                  })
                  .then(function(res) {
                    if (res.value == false) {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(further_help_tc);
                    } else {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(mental_health_101_tc);
                    }
                  });
              } else {
                return botui.message
                  .bot({
                    loading: true,
                    photo: polly,
                    delay: 3000,
                    content:
                      "Q2.請問你曾否經歷以下狀況:<br/><br/>" +
                      "- 自我傷害及/或傷害他人及/或暴力的意念和行為；<br/>及/或<br/><br/>" +
                      "- 因精神病患而入住醫院；<br/>及/或<br/><br/>" +
                      "- 經心理學家及/或精神科醫生及/或家庭醫一種或多於一種的精神病患，如: 抑鬱症/焦慮症/思覺失調/精神分裂症/人格障礙等<br/>及/或<br/><br/>" +
                      "- 正在服用醫生處方的精神科藥物",
                  })
                  .then(function() {
                    return botui.action.button({
                      addMessage: false,
                      action: [
                        { text: "有", value: true },
                        { text: "沒有", value: false },
                      ],
                    });
                  })
                  .then(function(res) {
                    if (res.value == false) {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(function() {
                          return botui.message.bot({
                            delay: 1000,
                            photo: polly,
                            content: "在進入線上聊天前，請填寫以下資訊:",
                          });
                        })
                        .then(function() {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "你的電話",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["contactNumber"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "你的電話是" + res.value, //? Personal contact number is
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "緊急聯絡人的名字",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["emergencyContactName"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "緊急聯絡人的名字是" + res.value, //? Emergency contact name is
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "與緊急聯絡人的關係",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["relationship"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "與緊急聯絡人的關係是" + res.value, //? Relationship is
                          });
                        })
                        .then(function(res) {
                          return botui.action.text({
                            addMessage: false,
                            action: {
                              size: 30,
                              placeholder: "緊急聯絡人的電話",
                            },
                          });
                        })
                        .then(function(res) {
                          personalInfo["emergencyContactNumber"] = res.value;
                          console.log(personalInfo);
                          return botui.message.add({
                            human: true,
                            photo: client,
                            content: "緊急聯絡人的電話是" + res.value, //? Emergency contact number is
                          });
                        })
                        .then(function() {
                          return botui.message.bot({
                            delay: 1000,
                            photo: polly,
                            content: "繼續在線聊天服務", //? Proceeding to Online Chat Service
                          });
                        })
                        .then(function() {
                          return botui.message.add({
                            delay: 1000,
                            photo: polly,
                            // TODO
                            content: "請稍等，我正在找輔導員與您聊天。", //? Please wait, I am now finding a counsellor to chat with you.
                          });
                        });
                      // .then(function() {
                      //   return botui.message.add({
                      //     delay: 3000,
                      //     photo: polly,
                      //     content:
                      //       '學生請點擊<a target="_blank" href="http://158.132.255.165:9988/chat/student?student_netid=21&staff_netid=10">鏈接</a>進入聊天室。', //? For student, please click the <a target="_blank" href="http://158.132.255.165:9988/chat/student?student_netid=21&staff_netid=10">link</a> to enter the chat room.
                      //   });
                      // })
                      // .then(function() {
                      //   return botui.message.add({
                      //     delay: 1000,
                      //     photo: polly,
                      //     content:
                      //       '[Demo only] 輔導員請點擊<a target="_blank" href="http://158.132.255.165:9988/chat/counsellor?student_netid=21&staff_netid=10">鏈接</a>進入聊天室。', //? For counsellor, please click the <a target="_blank" href="http://158.132.255.165:9988/chat/counsellor?student_netid=21&staff_netid=10">link</a> to enter the chat room.
                      //   });
                      // });
                    } else {
                      return botui.message
                        .human({
                          delay: 500,
                          photo: client,
                          content: res.text,
                        })
                        .then(function() {
                          return botui.message.bot({
                            loading: true,
                            delay: 2000,
                            photo: polly,
                            content:
                              "為了更全面地暸解你的需要，請預約輔導服務。",
                          });
                        })
                        .then(function() {
                          if (office_hour == true) {
                            return botui.message.bot({
                              loading: true,
                              delay: 1000,
                              photo: polly,
                              content:
                                '1. 在辦公時間內致電 (852)27666800 (星期一至五: 09.00 - 19.00, 星期六: 09.00 -12.00)<br/>2. 在辦公時間內前往 QT308 接待處作預約(入口在T棟)<br/>3. 電郵預約: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>4. 到網上系統<a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a>預約輔導服務</br>',
                            });
                          } else {
                            return botui.message.bot({
                              loading: true,
                              delay: 2000,
                              photo: polly,
                              content:
                                '1. 電郵預約: <a href=mailto:stud.counselling@polyu.edu.hk>stud.counselling@polyu.edu.hk</a><br/>2. 到網上系統<a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a>預約輔導服務</br>',
                            });
                          }
                        });
                    }
                  })
                  .then(end_tc);
              }
            });
        });
    }

    function emergency_support_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 1500,
          content:
            "<font color=black>在緊急情況下，請即致電999或到鄰近的急症室求助。</font>", //? In case of emergency, please Call 999 or go to the nearest emergency  / A&E service.
        })
        .then(function() {
          var office_hour = isSAOWorkingHours(new Date());
          if (office_hour == true) {
            contact_with_counsellors_tc();
          } else {
            return botui.message
              .bot({
                loading: true,
                photo: polly,
                delay: 1500,
                content:
                  "1. 與 PolyU-Line 輔導員聯絡: (852)81001583 <br>" + //? Contact with PolyU-Line Counsellors
                  "*所有電話將由 Vital Employee Service Consultancy Christian Family Service Centre 接聽。<br/><br/>" + //? All phone calls will be answered by Vital Employee Service Consultancy Christian Family Service Centre.
                  "2. 我們校園最近的公立醫院是：伊利沙伯醫院<br>" + //? The nearest public hospital of our campus is: Queen Elizabeth Hospital
                  "-香港九龍加士居道30號" +
                  "<br>-Tel: (852)35068888", //? 30 Gascoigne Road, Kowloon, Hong Kong
              })
              .then(further_help_tc);
          }
        });
    }

    function make_appointment_with_counsellors_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 1500,
          content:
            '1. 電郵預約: <a href="mailto:stud.counselling@polyu.edu.hk?subject=Making appointment with SAO counsellor&body=Dear Counsellor,%0D%0A%0D%0AI would like to make appointment with SAO counsellor on the following date and time:%0D%0ADate:________________%0D%0ATime: ________________%0D%0A%0D%0ALooking forward to your reply.%0D%0A%0D%0ARegards%0D%0A________________">stud.counselling@polyu.edu.hk</a><br/>2. 網上系統POSS預約輔導服務: <a href="https://www40.polyu.edu.hk/poss/secure/login/loginhome.do" target ="_blank">POSS</a></br>',
        })
        .then(further_help_tc);
    }

    function contact_with_counsellors_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 100,
          content:
            "1. 在辦公時間內致電: (852)27666800<br/>2. 在辦公時間內前往 QT308 接待處(入口在T棟)</br>",
        })
        .then(further_help_tc());
    }

    function polyu_line_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content:
            "立即與PolyU-Line輔導員聯絡: (852) 8100 1583<br/><br/>*基督教家庭服務中心（盈力僱員服務顧問）將會接聽所有電話。",
        })
        .then(further_help_tc());
    }

    function community_helpline_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content:
            '緊急求助電話號碼：(852)999<br/>社會福利署熱線：(852)23432255<br/>明愛向晴熱線：(852)18288<br/>生命熱線中心：(852)23820000<br/>撒瑪利亞會 － 24小時中文及多種語言防止自殺服務：(852)2896-0000<br/>賽馬會青少年情緒健康24小時網上支援平台「Open噏」：<a href="www.openup.hk" target ="_blank">www.openup.hk</a><br/>',
        })
        .then(further_help_tc());
    }

    function further_help_tc() {
      return botui.message
        .bot({
          loading: true,
          photo: polly,
          delay: 3000,
          content: "多謝你使用我們的服務。請問你還有其他需要嗎?",
        })
        .then(function() {
          return botui.action
            .button({
              addMessage: false,
              action: [
                { text: "我仍需要其他服務。", value: true },
                { text: "不需要了，謝謝。", value: false },
              ],
            })
            .then(function(res) {
              if (res.value == true) {
                if (service_list == true || finish_assessment == false) {
                  botui.message
                    .human({
                      delay: 500,
                      photo: client,
                      content: res.text,
                    })
                    .then(init_choices_tc);
                  return;
                }

                if (score <= 10) {
                  return botui.message
                    .human({
                      photo: client,
                      delay: 500,
                      content: res.text,
                    })
                    .then(mid_recommendations_tc);
                } else {
                  return botui.message
                    .human({
                      photo: client,
                      delay: 500,
                      content: res.text,
                    })
                    .then(high_recommendations_tc);
                }
              } else {
                return botui.message
                  .human({
                    photo: client,
                    delay: 500,
                    content: res.text,
                  })
                  .then(function() {
                    if (score > 10 || service_list == true) {
                      botui.message.bot({
                        loading: true,
                        photo: polly,
                        delay: 1000,
                        content: (content =
                          "<font color=black>如果你正身處緊急情況或/及險境，並有感自身及/或他人有即時的生命危險，請即致電999或到鄰近的急症室求助。</font>"),
                      });
                    }
                  })
                  .then(end_tc);
              }
            });
        });
    }

    function end_tc() {
      rating_tc();
    }

    function rating_tc() {
      botui.message
        .add({
          type: "html",
          delay: 1000,
          photo: polly,
          content:
            "<p>請分享你對本服務的體驗:</p >" +
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
        .then(function() {
          botui.action
            .button({
              addMessage: false,
              photo: client,
              action: [
                {
                  text: "提交",
                },
              ],
            })
            .then(function() {
              // fix the stars
              console.log($(".far"));

              $(".far").removeClass("available");
              botui.message.bot({
                loading: true,
                delay: 1000,
                photo: polly,
                content: "感謝你寶貴的意見!",
              });
            });
        })
        .then(_close);
    }

    const addToQueue = async (student_netid) => {
      const response = await $.ajax({
        url: "/main/api/addstud/",
        method: "POST",
        data: {
          student_netid: student_netid,
        },
      });

      if (response.status == "success") {
        return Promise.resolve(response.message);
      } else {
        return Promise.reject(response.message);
      }
    };

    const getQueueStatus = async (student_netid) => {
      return await $.ajax({
        url: "/main/debug/getseq/",
        method: "GET",
        data: {
          student_netid: student_netid,
        },
      });
    };

    const quitQueue = async (student_netid) => {
      return await $.ajax({
        url: "/main/debug/deletestud/",
        method: "POST",
        data: {
          student_netid: student_netid,
        },
      });
    };

    const getStatusByStudentNetId = async (student_netid) => {
      return await $.ajax({
        url: "/main/debug/getstud/",
        method: "GET",
        data: {
          student_netid: student_netid,
        },
      });
    };

    const waitSubsribe = async (student_netid, waitingNo) => {
      await botui.message.add({
        delay: 1000,
        photo: polly,
        content:
          "Sorry, there is no counsellor available right now, do you want to wait until our counsellor available, or you may contact us directly at 27666800.",
      });

      const actionResult = await botui.action.button({
        addMessage: false,
        action: [
          { text: "Wait", value: true },
          { text: "Quit", value: false },
        ],
      });

      // quit
      if (!actionResult.value) {
        await quitQueue(student_netid);
        throw new Error(
          "Thank you for using our service, you may make an appointment with our counsellor via POSS or call 2766 6800 if needed."
        );
      } else {
        // wait
        await botui.message.add({
          delay: 1000,
          photo: polly,
          content: `Your waiting no. is ${waitingNo +
            1}, I will redirect you to our counsellor as soon as possible.`,
        });
      }
    };
  }
})();
