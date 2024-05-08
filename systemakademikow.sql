-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Хост: 127.0.0.1
-- Час створення: Січ 30 2024 р., 05:42
-- Версія сервера: 10.4.32-MariaDB
-- Версія PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База даних: `systemakademikow`
--

-- --------------------------------------------------------

--
-- Структура таблиці `akademiki`
--

CREATE TABLE `akademiki` (
  `SymbolA` varchar(10) NOT NULL,
  `NazwaA` varchar(30) DEFAULT NULL,
  `Adres` varchar(100) DEFAULT NULL,
  `LiczbaPokoi` int(11) DEFAULT NULL,
  `Status` enum('Otwarty','Zamknięty','Na remoncie','W budowie') DEFAULT 'Otwarty',
  `Uwagi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп даних таблиці `akademiki`
--

INSERT INTO `akademiki` (`SymbolA`, `NazwaA`, `Adres`, `LiczbaPokoi`, `Status`, `Uwagi`) VALUES
('T-15', 'Ikarus', 'Wittiga 6', 240, 'Otwarty', ''),
('T-16', '', 'Wittiga 4', 0, 'Zamknięty', ''),
('T-17', 'AkademikBEST', 'Wróblewskiego 27', 240, 'Otwarty', '');

-- --------------------------------------------------------

--
-- Структура таблиці `mieszkancy`
--

CREATE TABLE `mieszkancy` (
  `IdM` int(11) NOT NULL,
  `Nazwisko` varchar(50) DEFAULT NULL,
  `Imie` varchar(50) DEFAULT NULL,
  `Indeks` int(6) UNSIGNED NOT NULL,
  `IdA` varchar(10) DEFAULT NULL,
  `Pokoj` int(4) UNSIGNED NOT NULL,
  `Telefon` varchar(12) DEFAULT NULL,
  `E_mail` varchar(50) DEFAULT NULL,
  `Uwagi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп даних таблиці `mieszkancy`
--

INSERT INTO `mieszkancy` (`IdM`, `Nazwisko`, `Imie`, `Indeks`, `IdA`, `Pokoj`, `Telefon`, `E_mail`, `Uwagi`) VALUES
(6, 'Bondarenko', 'Oleksandr', 266123, 'T-17', 612, '769526021', 'bond.olek@gmail.com', ''),
(7, 'Ranchukova', 'Zlata', 266821, 'T-17', 818, '+48794186003', 'zlata.ranch91@gmail.com', ''),
(8, 'Hancharyk', 'Ivan', 266111, 'T-17', 818, '+48001001002', '111@gmail.com', ''),
(9, 'Szymański', 'Jakub', 268943, 'T-15', 419, '', 'szym_j4kub@gmail.com', ''),
(10, 'Woźniak', 'Maja', 260348, 'T-15', 521, '345210059', '', '');

-- --------------------------------------------------------

--
-- Структура таблиці `pracownicy`
--

CREATE TABLE `pracownicy` (
  `IdP` int(11) NOT NULL,
  `Nazwisko` varchar(50) DEFAULT NULL,
  `Imie` varchar(50) DEFAULT NULL,
  `Stanowisko` enum('Dyrektor','Kierownik','Portier') DEFAULT 'Portier',
  `IdA` varchar(10) DEFAULT NULL,
  `DUr` date DEFAULT NULL,
  `DZatr` date DEFAULT NULL,
  `Pensja` decimal(10,2) DEFAULT NULL,
  `Pensum` decimal(5,2) DEFAULT NULL,
  `Telefon` varchar(12) DEFAULT NULL,
  `E_mail` varchar(50) DEFAULT NULL,
  `Login` varchar(50) DEFAULT NULL,
  `Haslo` varchar(50) DEFAULT NULL,
  `Uwagi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп даних таблиці `pracownicy`
--

INSERT INTO `pracownicy` (`IdP`, `Nazwisko`, `Imie`, `Stanowisko`, `IdA`, `DUr`, `DZatr`, `Pensja`, `Pensum`, `Telefon`, `E_mail`, `Login`, `Haslo`, `Uwagi`) VALUES
(20, 'Nowak', 'Patrycja', 'Dyrektor', NULL, '1990-10-09', '2019-06-01', 6500.00, 160.00, '+48159753456', 'qwerty@pwr', 'Patrycja_Nowak', '1234567890', NULL),
(21, 'Knura', 'Magdalena', 'Kierownik', 'T-17', '2005-05-12', '2024-01-01', 0.00, 120.00, '+48794186003', 'magda.Knura@gmail.com', 'Magdalena_Knura', '1234567890', ''),
(22, 'Nowak', 'Kamil', 'Portier', 'T-15', '1965-07-08', '2014-11-01', 3692.74, 200.00, '+48769526021', '', 'Kamil_Nowak', '1234567890', 'pierwszy dodany portier'),
(23, 'Nowak', 'Kamil', 'Kierownik', 'T-15', '1968-08-31', '2016-04-03', 3884.49, 160.00, '+48001001001', 'example@gmail.com', 'Kamil_Nowak_2', '1234567890', ''),
(24, 'Szymańska', 'Katarzyna', 'Dyrektor', NULL, '1989-11-24', '2021-08-12', 0.00, 120.00, '', 'example@gmail.com', 'Katarzyna_Szymańska', '1234567890', ''),
(25, 'Zieliński', 'Michał', 'Portier', 'T-17', '0000-00-00', '2023-09-01', 2039.45, 80.00, '', 'example@gmail.com', 'Michał_Zieliński', '1234567890', ''),
(26, 'Kowalczyk', 'Alicja', 'Portier', 'T-17', '1954-08-25', '0000-00-00', 0.00, 80.00, '769526021', '', 'Alicja_Kowalczyk', '1234567890', ''),
(27, 'Wiśniewski', 'Piotr', 'Portier', 'T-15', '0000-00-00', '0000-00-00', 0.00, 0.00, '', '', 'Piotr_Wiśniewski', '1234567890', 'Nie do końca uzupełnione konto');

-- --------------------------------------------------------

--
-- Структура таблиці `usterki`
--

CREATE TABLE `usterki` (
  `IdU` int(11) NOT NULL,
  `IdA` varchar(10) DEFAULT NULL,
  `Pokoj` int(11) DEFAULT NULL,
  `DZgloszenia` date DEFAULT NULL,
  `Status` enum('Nowa','W trakcie','Naprawiona') DEFAULT 'Nowa',
  `Opis` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Дамп даних таблиці `usterki`
--

INSERT INTO `usterki` (`IdU`, `IdA`, `Pokoj`, `DZgloszenia`, `Status`, `Opis`) VALUES
(5, 'T-17', 818, '2024-01-28', 'Nowa', 'Awaria prysznica'),
(6, 'T-17', 0, '2024-01-30', 'Nowa', 'Złamana winda B'),
(7, 'T-17', 319, '2024-01-04', 'Naprawiona', 'Nie działa lodówka'),
(8, 'T-17', 908, '2024-01-25', 'W trakcie', 'Problem z regulacją temperatury ogrzewania'),
(9, 'T-15', 0, '2024-01-28', 'Nowa', 'Nie działa winda');

--
-- Індекси збережених таблиць
--

--
-- Індекси таблиці `akademiki`
--
ALTER TABLE `akademiki`
  ADD PRIMARY KEY (`SymbolA`);

--
-- Індекси таблиці `mieszkancy`
--
ALTER TABLE `mieszkancy`
  ADD PRIMARY KEY (`IdM`),
  ADD UNIQUE KEY `index` (`Indeks`),
  ADD KEY `IdA` (`IdA`);

--
-- Індекси таблиці `pracownicy`
--
ALTER TABLE `pracownicy`
  ADD PRIMARY KEY (`IdP`),
  ADD KEY `FK_IdA` (`IdA`);

--
-- Індекси таблиці `usterki`
--
ALTER TABLE `usterki`
  ADD PRIMARY KEY (`IdU`),
  ADD KEY `IdA` (`IdA`);

--
-- AUTO_INCREMENT для збережених таблиць
--

--
-- AUTO_INCREMENT для таблиці `mieszkancy`
--
ALTER TABLE `mieszkancy`
  MODIFY `IdM` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT для таблиці `pracownicy`
--
ALTER TABLE `pracownicy`
  MODIFY `IdP` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT для таблиці `usterki`
--
ALTER TABLE `usterki`
  MODIFY `IdU` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Обмеження зовнішнього ключа збережених таблиць
--

--
-- Обмеження зовнішнього ключа таблиці `mieszkancy`
--
ALTER TABLE `mieszkancy`
  ADD CONSTRAINT `IdA` FOREIGN KEY (`IdA`) REFERENCES `akademiki` (`SymbolA`);

--
-- Обмеження зовнішнього ключа таблиці `pracownicy`
--
ALTER TABLE `pracownicy`
  ADD CONSTRAINT `FK_IdA` FOREIGN KEY (`IdA`) REFERENCES `akademiki` (`SymbolA`);

--
-- Обмеження зовнішнього ключа таблиці `usterki`
--
ALTER TABLE `usterki`
  ADD CONSTRAINT `usterki_ibfk_1` FOREIGN KEY (`IdA`) REFERENCES `akademiki` (`SymbolA`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
