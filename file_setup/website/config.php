<?php
// config.php - การเชื่อมต่อฐานข้อมูล
$host = 'localhost';
$dbname = 'student_db';
$username = 'root'; // เปลี่ยนตามการตั้งค่าของคุณ
$password = '';     // เปลี่ยนตามการตั้งค่าของคุณ

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    die("เชื่อมต่อฐานข้อมูลไม่สำเร็จ: " . $e->getMessage());
}
?>