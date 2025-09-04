-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 04, 2025 at 09:52 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `student_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `student_name` varchar(100) NOT NULL,
  `student_nickname` varchar(50) NOT NULL,
  `parent_name` varchar(100) NOT NULL,
  `parent_car_plate` varchar(20) DEFAULT NULL,
  `parent_phone` varchar(20) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `student_name`, `student_nickname`, `parent_name`, `parent_car_plate`, `parent_phone`, `status`) VALUES
(1, 'ณัฐวุฒิ สายใจ', 'วุฒิ', 'อนันต์ ใจดี', '6ขต325กรุงเทพมหานคร', '0891112233', 1),
(2, 'ปาริชาติ ดารา', 'ริช', 'ศักดา แสงทอง', 'ขง2886เชียงราย', '0882223344', 1),
(3, 'ชลธิชา รุ่งเรือง', 'ชล', 'มนตรี รุ่งเรือง', 'บห9623ศรีสะเกษ', '0873334455', 1),
(4, 'ธนกร พิทักษ์', 'กร', 'วิเชียร สายลม', '5กค198กรุงเทพมหานคร', '0864445566', 1),
(5, 'นรีกานต์ คำแสง', 'นรี', 'ไพศาล มณีรัตน์', 'จพ911เชียงใหม่', '0855556677', 1),
(6, 'ภูริวัฒน์ อารักษ์', 'ภู', 'สมศักดิ์ พูลสุข', 'งค345เชียงใหม่', '0846667788', 1),
(7, 'ลองระบบ', 'ลอง', 'ทดสอบ นะครับ', 'ขท555เชียงใหม่', '0837426067', 0),
(8, 'อีสูสู ซิ่งจัด', 'ออนิว', 'วัยรุ่น สร้างตัว', 'ขย3487เชียงใหม่', '0888988987', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
