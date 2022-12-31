USE pill;
CREATE TABLE users (id INTEGER PRIMARY KEY AUTO_INCREMENT, username TEXT, name TEXT, email TEXT, password TEXT, idcard TEXT);

INSERT INTO users (username, name, email, password, idcard) VALUES ("shap", "shap", "shap@hotmail.com", "$2b$12$1ezdGlmUa3E7nEJ59TU09.lwzo7tHT3loYerXF/hJP1BxcRf8upVa",  "130223000033330303")

CREATE TABLE posts (id INTEGER PRIMARY KEY AUTO_INCREMENT, from_user_id INTEGER, to_user_id INTEGER, medicine_name TEXT, quantity INTEGER, status TEXT);

INSERT INTO posts (from_user_id, medicine_name, quantity, status) VALUES (1, "布洛芬", 5, "available");
INSERT INTO posts (from_user_id, medicine_name, quantity, status) VALUES (7, "布洛芬", 10, "available");
INSERT INTO posts (from_user_id, medicine_name, quantity, status) VALUES (12, "布洛芬", 12, "available");
INSERT INTO posts (from_user_id, medicine_name, quantity, status) VALUES (13, "鸡蛋", 1, "available");