<?php
// delete.php - หน้าลบข้อมูลนักเรียน
require_once 'config.php';

// ตรวจสอบว่ามี ID ส่งมาหรือไม่
if (!isset($_GET['id']) || !is_numeric($_GET['id'])) {
    header('Location: index.php');
    exit();
}

$student_id = $_GET['id'];
$message = '';
$message_type = '';

// ดึงข้อมูลนักเรียนก่อนลบ
try {
    $stmt = $pdo->prepare("SELECT * FROM students WHERE id = ? AND status = 1");
    $stmt->execute([$student_id]);
    $student = $stmt->fetch();
    
    if (!$student) {
        header('Location: index.php?error=student_not_found');
        exit();
    }
    
    // ทำการลบ (อัพเดทสถานะเป็น 0)
    $stmt = $pdo->prepare("UPDATE students SET status = 0 WHERE id = ?");
    $stmt->execute([$student_id]);
    
    $message = "ลบข้อมูลของ " . htmlspecialchars($student['student_name']) . " เรียบร้อยแล้ว";
    $message_type = "success";
    
} catch(PDOException $e) {
    $message = "เกิดข้อผิดพลาดในการลบข้อมูล: " . $e->getMessage();
    $message_type = "error";
}

// เปลี่ยนเส้นทางกลับไปหน้าหลักพร้อมข้อความ
$redirect_url = "index.php?message=" . urlencode($message) . "&type=" . $message_type;
header("Location: $redirect_url");
exit();
?>