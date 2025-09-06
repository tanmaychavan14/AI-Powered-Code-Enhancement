/**
 * @jest-environment jsdom
 */

describe('renderMessage', () => {
  let app;
  let messageContainer;

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="app">
        <div class="chat-screen">
          <div class="messages"></div>
        </div>
      </div>
    `;
    app = document.querySelector(".app");
    messageContainer = app.querySelector(".chat-screen .messages");
  });

  it('should render a "my" message correctly', () => {
    const message = { username: 'testUser', text: 'Hello from me!' };
    renderMessage("my", message);
    expect(messageContainer.children.length).toBe(1);
    expect(messageContainer.firstChild.classList.contains('my-message')).toBe(true);
    expect(messageContainer.firstChild.innerHTML).toContain('You');
    expect(messageContainer.firstChild.innerHTML).toContain('Hello from me!');
  });

  it('should render an "other" message correctly', () => {
    const message = { username: 'otherUser', text: 'Hello from them!' };
    renderMessage("other", message);
    expect(messageContainer.children.length).toBe(1);
    expect(messageContainer.firstChild.classList.contains('other-message')).toBe(true);
    expect(messageContainer.firstChild.innerHTML).toContain('otherUser');
    expect(messageContainer.firstChild.innerHTML).toContain('Hello from them!');
  });

  it('should render an "update" message correctly', () => {
    const message = 'User joined the chat';
    renderMessage("update", message);
    expect(messageContainer.children.length).toBe(1);
    expect(messageContainer.firstChild.classList.contains('update')).toBe(true);
    expect(messageContainer.firstChild.textContent).toBe('User joined the chat');
  });

  it('should handle empty message text correctly', () => {
    const message = { username: 'testUser', text: '' };
    renderMessage("my", message);
    expect(messageContainer.children.length).toBe(1);
    expect(messageContainer.firstChild.innerHTML).toContain('<div class="text"></div>');
  });

  it('should handle null message correctly', () => {
    renderMessage("update", null);
    expect(messageContainer.children.length).toBe(1);
    expect(messageContainer.firstChild.textContent).toBe('null');
  });

  function renderMessage(type, message) {
    let messageContainer = app.querySelector(".chat-screen .messages");
    if (type == "my") {
      let el = document.createElement("div");
      el.setAttribute("class", "message my-message");
      el.innerHTML = `
        <div>
          <div class ="name">You</div>
          <div class="text">${message.text}</div>
        </div>`;
      messageContainer.appendChild(el);
    }
    else if (type == "other") {
      let el = document.createElement("div");
      el.setAttribute("class", "message other-message");
      el.innerHTML = `
            <div>
                <div class ="name">${message.username}</div>
                <div class="text">${message.text}</div>
            </div>`;
      messageContainer.appendChild(el);
    }
    else if (type == "update") {
      let el = document.createElement("div");
      el.setAttribute("class", "update");
      el.innerText = message;
      messageContainer.appendChild(el);
    }
    messageContainer.scrollTop = messageContainer.scrollHeight - messageContainer.clientHeight;
  }
});

describe('Event Listeners', () => {
  let app;
  let socket;

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="app">
        <div class="join-screen active">
          <input type="text" id="username" value="">
          <button id="join-user"></button>
        </div>
        <div class="chat-screen">
          <input type="text" id="message-input" value="">
          <button id="send-message"></button>
          <button id="exit-chat"></button>
          <div class="messages"></div>
        </div>
      </div>
    `;
    app = document.querySelector(".app");

    // Mock socket.io
    socket = {
      emit: jest.fn(),
      on: jest.fn(),
    };

    // Mock io function to return the mocked socket object
    global.io = jest.fn(() => socket);

    // Initialize the chat application (run the provided code)
    (function () {
      const app = document.querySelector(".app");
      const socket = io();
      let uname;
      app.querySelector(".join-screen #join-user").addEventListener("click", function () {
        let username = app.querySelector(".join-screen #username").value;
        if (username.length == 0) {
          return;
        }
        socket.emit("newuser", username);
        uname = username;
        app.querySelector(".join-screen").classList.remove("active");
        app.querySelector(".chat-screen").classList.add("active");
      });
      app.querySelector(".chat-screen #send-message").addEventListener("click", function () {
        let message = app.querySelector(".chat-screen #message-input").value;
        if (message.length == 0) {
          return;
        }
        renderMessage("my", {
          username: uname,
          text: message
        });
        socket.emit("chat", {
          username: uname,
          text: message
        });
        app.querySelector(".chat-screen #message-input").value = "";
      });
      app.querySelector(".chat-screen #exit-chat").addEventListener("click", function () {
        socket.emit("exituser", uname);
        window.location.href = window.location.href;
      });
      socket.on("update", function (update) {
        renderMessage("update", update);
      })
      socket.on("chat", function (message) {
        renderMessage("other", message);
      })
      function renderMessage(type, message) {
        let messageContainer = app.querySelector(".chat-screen .messages");
        if (type == "my") {
          let el = document.createElement("div");
          el.setAttribute("class", "message my-message");
          el.innerHTML = `
        <div>
            <div class ="name">You</div>
            <div class="text">${message.text}</div>
        </div>`;
          messageContainer.appendChild(el);
        }
        else if (type == "other") {
          let el = document.createElement("div");
          el.setAttribute("class", "message other-message");
          el.innerHTML = `
            <div>
                <div class ="name">${message.username}</div>
                <div class="text">${message.text}</div>
            </div>`;
          messageContainer.appendChild(el);
        }
        else if (type == "update") {
          let el = document.createElement("div");
          el.setAttribute("class", "update");
          el.innerText = message;
          messageContainer.appendChild(el);
        }
        messageContainer.scrollTop = messageContainer.scrollHeight - messageContainer.clientHeight;
      }

    })();
  });

  afterEach(() => {
    // Restore mocks
    jest.restoreAllMocks();
  });

  it('should emit "newuser" event on join-user click with a valid username', () => {
    const usernameInput = app.querySelector(".join-screen #username");
    const joinButton = app.querySelector(".join-screen #join-user");
    usernameInput.value = 'testUser';
    joinButton.click();
    expect(socket.emit).toHaveBeenCalledWith('newuser', 'testUser');
    expect(app.querySelector(".join-screen").classList.contains("active")).toBe(false);
    expect(app.querySelector(".chat-screen").classList.contains("active")).toBe(true);
  });

  it('should not emit "newuser" event on join-user click with an empty username', () => {
    const joinButton = app.querySelector(".join-screen #join-user");
    joinButton.click();
    expect(socket.emit).not.toHaveBeenCalled();
    expect(app.querySelector(".join-screen").classList.contains("active")).toBe(true);
    expect(app.querySelector(".chat-screen").classList.contains("active")).toBe(false);
  });

  it('should emit "chat" event on send-message click with a valid message', () => {
    // Simulate joining the chat first
    const usernameInput = app.querySelector(".join-screen #username");
    const joinButton = app.querySelector(".join-screen #join-user");
    usernameInput.value = 'testUser';
    joinButton.click();

    const messageInput = app.querySelector(".chat-screen #message-input");
    const sendButton = app.querySelector(".chat-screen #send-message");
    messageInput.value = 'Hello, world!';
    sendButton.click();
    expect(socket.emit).toHaveBeenCalledWith('chat', { username: 'testUser', text: 'Hello, world!' });
    expect(messageInput.value).toBe("");
  });

  it('should not emit "chat" event on send-message click with an empty message', () => {
    // Simulate joining the chat first
    const usernameInput = app.querySelector(".join-screen #username");
    const joinButton = app.querySelector(".join-screen #join-user");
    usernameInput.value = 'testUser';
    joinButton.click();

    const sendButton = app.querySelector(".chat-screen #send-message");
    sendButton.click();
    expect(socket.emit).not.toHaveBeenCalled();
  });

  it('should emit "exituser" event on exit-chat click', () => {
    // Simulate joining the chat first
    const usernameInput = app.querySelector(".join-screen #username");
    const joinButton = app.querySelector(".join-screen #join-user");
    usernameInput.value = 'testUser';
    joinButton.click();

    const exitButton = app.querySelector(".chat-screen #exit-chat");
    global.window = Object.create(window);
    const url = "http://localhost";
    Object.defineProperty(window, 'location', {
      value: {
        href: url
      }
    });
    exitButton.click();
    expect(socket.emit).toHaveBeenCalledWith('exituser', 'testUser');
    expect(window.location.href).toEqual(url);
  });

  it('should call renderMessage when "update" event is received', () => {
    const updateHandler = socket.on.mock.calls.find(call => call[0] === 'update')[1];
    const renderMessageMock = jest.fn();
    // Mock renderMessage in the scope of updateHandler
    (function () {
      const app = document.querySelector(".app");
      const socket = io();
      let uname;
      app.querySelector(".join-screen #join-user").addEventListener("click", function () {
        let username = app.querySelector(".join-screen #username").value;
        if (username.length == 0) {
          return;
        }
        socket.emit("newuser", username);
        uname = username;
        app.querySelector(".join-screen").classList.remove("active");
        app.querySelector(".chat-screen").classList.add("active");
      });
      app.querySelector(".chat-screen #send-message").addEventListener("click", function () {
        let message = app.querySelector(".chat-screen #message-input").value;
        if (message.length == 0) {
          return;
        }
        renderMessage("my", {
          username: uname,
          text: message
        });
        socket.emit("chat", {
          username: uname,
          text: message
        });
        app.querySelector(".chat-screen #message-input").value = "";
      });
      app.querySelector(".chat-screen #exit-chat").addEventListener("click", function () {
        socket.emit("exituser", uname);
        window.location.href = window.location.href;
      });
      socket.on("update", function (update) {
        renderMessage("update", update);
      })
      socket.on("chat", function (message) {
        renderMessage("other", message);
      })
      function renderMessage(type, message) {
        renderMessageMock(type, message);
        let messageContainer = app.querySelector(".chat-screen .messages");
        if (type == "my") {
          let el = document.createElement("div");
          el.setAttribute("class", "message my-message");
          el.innerHTML = `
        <div>
            <div class ="name">You</div>
            <div class="text">${message.text}</div>
        </div>`;
          messageContainer.appendChild(el);
        }
        else if (type == "other") {
          let el = document.createElement("div");
          el.setAttribute("class", "message other-message");
          el.innerHTML = `
            <div>
                <div class ="name">${message.username}</div>
                <div class="text">${message.text}</div>
            </div>`;
          messageContainer.appendChild(el);
        }
        else if (type == "update") {
          let el = document.createElement("div");
          el.setAttribute("class", "update");
          el.innerText = message;
          messageContainer.appendChild(el);
        }
        messageContainer.scrollTop = messageContainer.scrollHeight - messageContainer.clientHeight;
      }

    })();

    updateHandler('User joined');
    expect(renderMessageMock).toHaveBeenCalledWith('update', 'User joined');
  });

  it('should call renderMessage when "chat" event is received', () => {
    const chatHandler = socket.on.mock.calls.find(call => call[0] === 'chat')[1];
    const renderMessageMock = jest.fn();
        // Mock renderMessage in the scope of chatHandler
        (function () {
          const app = document.querySelector(".app");
          const socket = io();
          let uname;
          app.querySelector(".join-screen #join-user").addEventListener("click", function () {
            let username = app.querySelector(".join-screen #username").value;
            if (username.length == 0) {
              return;
            }
            socket.emit("newuser", username);
            uname = username;
            app.querySelector(".join-screen").classList.remove("active");
            app.querySelector(".chat-screen").classList.add("active");
          });
          app.querySelector(".chat-screen #send-message").addEventListener("click", function () {
            let message = app.querySelector(".chat-screen #message-input").value;
            if (message.length == 0) {
              return;
            }
            renderMessage("my", {
              username: uname,
              text: message
            });
            socket.emit("chat", {
              username: uname,
              text: message
            });
            app.querySelector(".chat-screen #message-input").value = "";
          });
          app.querySelector(".chat-screen #exit-chat").addEventListener("click", function () {
            socket.emit("exituser", uname);
            window.location.href = window.location.href;
          });
          socket.on("update", function (update) {
            renderMessage("update", update);
          })
          socket.on("chat", function (message) {
            renderMessage("other", message);
          })
          function renderMessage(type, message) {
            renderMessageMock(type, message);
            let messageContainer = app.querySelector(".chat-screen .messages");
            if (type == "my") {
              let el = document.createElement("div");
              el.setAttribute("class", "message my-message");
              el.innerHTML = `
            <div>
                <div class ="name">You</div>
                <div class="text">${message.text}</div>
            </div>`;
              messageContainer.appendChild(el);
            }
            else if (type == "other") {
              let el = document.createElement("div");
              el.setAttribute("class", "message other-message");
              el.innerHTML = `
                <div>
                    <div class ="name">${message.username}</div>
                    <div class="text">${message.text}</div>
                </div>`;
              messageContainer.appendChild(el);
            }
            else if (type == "update") {
              let el = document.createElement("div");
              el.setAttribute("class", "update");
              el.innerText = message;
              messageContainer.appendChild(el);
            }
            messageContainer.scrollTop = messageContainer.scrollHeight - messageContainer.clientHeight;
          }
    
        })();
    const message = { username: 'anotherUser', text: 'Hello!' };
    chatHandler(message);
    expect(renderMessageMock).toHaveBeenCalledWith('other', message);
  });
});