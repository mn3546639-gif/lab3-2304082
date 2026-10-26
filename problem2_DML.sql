USE library;
INSERT INTO AUTHOR (author_id, name, country) VALUES
(1, 'Naguib Mahfouz', 'Egypt'),
(2, 'George Orwell', 'United Kingdom'),
(3, 'Jane Austen', 'United Kingdom');
INSERT INTO BOOK (book_id, title, price, author_id) VALUES
(1, 'Palace Walk', 15.00, 1),
(2, 'The Thief and the Dogs', 12.50, 1),
(3, '1984', 18.00, 2),
(4, 'Animal Farm', 10.00, 2),
(5, 'Pride and Prejudice', 16.00, 3),
(6, 'Emma', 14.50, 3);
