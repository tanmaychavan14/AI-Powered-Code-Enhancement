const { createServer } = require("http");
const { Server } = require("socket.io");
const Client = require("socket.io-client");

describe("Socket.IO Server Tests", () => {
  let io, server, socket, client;

  beforeAll((done) => {
    server = createServer();
    io = new Server(server);
    server.listen(() => {
      const port = server.address().port;
      client = new Client(`http://localhost:${port}`);

      io.on("connection", (socket) => {
        global.socket = socket;

        socket.on("newuser", function (username) {
          socket.broadcast.emit("update", username + "Joined the conversation");
        });

        socket.on("exituser", function (username) {
          socket.broadcast.emit("update", username + "left the conversation");
        });

        socket.on("chat", function (message) {
          socket.broadcast.emit("chat", message);
        });
      });

      client.on("connect", done);
    });
  });

  afterAll(() => {
    io.close();
    client.close();
  });

  describe("on('newuser', function(username))", () => {
    test("should broadcast 'update' event with correct message on 'newuser'", (done) => {
      const username = "testUser";
      client.on("update", (message) => {
        expect(message).toBe(username + "Joined the conversation");
        done();
      });
      socket.emit("newuser", username);
    });

    test("should handle empty username without errors", (done) => {
      client.on("update", (message) => {
        expect(message).toBe("Joined the conversation");
        done();
      });
      socket.emit("newuser", "");
    });

    test("should handle username with special characters", (done) => {
      const username = "testUser!@#$%^&*()_+";
      client.on("update", (message) => {
        expect(message).toBe(username + "Joined the conversation");
        done();
      });
      socket.emit("newuser", username);
    });
  });

  describe("on('exituser', function(username))", () => {
    test("should broadcast 'update' event with correct message on 'exituser'", (done) => {
      const username = "testUser";
      client.on("update", (message) => {
        expect(message).toBe(username + "left the conversation");
        done();
      });
      socket.emit("exituser", username);
    });

    test("should handle empty username without errors", (done) => {
        client.on("update", (message) => {
          expect(message).toBe("left the conversation");
          done();
        });
        socket.emit("exituser", "");
      });

    test("should handle username with numbers", (done) => {
      const username = "user123";
      client.on("update", (message) => {
        expect(message).toBe(username + "left the conversation");
        done();
      });
      socket.emit("exituser", username);
    });
  });

  describe("on('chat', function(message))", () => {
    test("should broadcast 'chat' event with the message", (done) => {
      const message = "Hello, world!";
      client.on("chat", (receivedMessage) => {
        expect(receivedMessage).toBe(message);
        done();
      });
      socket.emit("chat", message);
    });

    test("should handle an empty message without errors", (done) => {
      client.on("chat", (receivedMessage) => {
        expect(receivedMessage).toBe("");
        done();
      });
      socket.emit("chat", "");
    });

    test("should handle message with special characters and numbers", (done) => {
      const message = "Message123!@#$%^&*()_+";
      client.on("chat", (receivedMessage) => {
        expect(receivedMessage).toBe(message);
        done();
      });
      socket.emit("chat", message);
    });
  });
});