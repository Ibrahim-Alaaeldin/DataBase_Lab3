USE library;

INSERT INTO AUTHOR (author_id, name, country) VALUES
  (1, 'Naguib Mahfouz', 'Egypt'),
  (2, 'Agatha Christie', 'United Kingdom'),
  (3, 'Paulo Coelho', 'Brazil');

INSERT INTO BOOK (book_id, title, price, author_id) VALUES
  (1, 'Palace Walk', 15.50, 1),
  (2, 'The Thief and the Dogs', 12.00, 1),
  (3, 'Murder on the Orient Express', 18.75, 2),
  (4, 'And Then There Were None', 16.00, 2),
  (5, 'The Alchemist', 14.25, 3),
  (6, 'Eleven Minutes', 17.90, 3);
