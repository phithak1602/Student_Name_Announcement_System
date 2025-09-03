<?php
// edit.php - หน้าแก้ไขข้อมูลนักเรียน
require_once 'config.php';

$success = '';
$error = '';
$student = null;

// ตรวจสอบว่ามี ID ส่งมาหรือไม่
if (!isset($_GET['id']) || !is_numeric($_GET['id'])) {
    header('Location: index.php');
    exit();
}

$student_id = $_GET['id'];

// ดึงข้อมูลนักเรียนที่ต้องการแก้ไข
try {
    $stmt = $pdo->prepare("SELECT * FROM students WHERE id = ? AND status = 1");
    $stmt->execute([$student_id]);
    $student = $stmt->fetch();
    
    if (!$student) {
        $error = "ไม่พบข้อมูลนักเรียนที่ต้องการแก้ไข";
    }
} catch(PDOException $e) {
    $error = "เกิดข้อผิดพลาด: " . $e->getMessage();
}

// ประมวลผลฟอร์มเมื่อมีการส่งข้อมูล
if ($_SERVER['REQUEST_METHOD'] == 'POST' && $student) {
    $student_name = trim($_POST['student_name']);
    $student_nickname = trim($_POST['student_nickname']);
    $parent_name = trim($_POST['parent_name']);
    $parent_car_plate = trim($_POST['parent_car_plate']);
    $parent_phone = trim($_POST['parent_phone']);
    
    // ตรวจสอบข้อมูลที่จำเป็น
    if (empty($student_name) || empty($student_nickname) || empty($parent_name)|| empty($parent_car_plate)|| empty($parent_phone)) {
        $error = "กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน";
    } else {
        try {
            // ตรวจสอบชื่อเล่นซ้ำ (ยกเว้นนักเรียนคนเดิม)
            $stmt = $pdo->prepare("SELECT id FROM students WHERE student_nickname = ? AND id != ? AND status = 1");
            $stmt->execute([$student_nickname, $student_id]);
            $existing_student = $stmt->fetch();
            
            if ($existing_student) {
                $error = "ชื่อเล่น \"" . htmlspecialchars($student_nickname) . "\" มีนักเรียนคนอื่นใช้แล้ว กรุณาใช้ชื่อเล่นอื่น";
            } else {
                // อัพเดทข้อมูลในฐานข้อมูล
                $stmt = $pdo->prepare("UPDATE students SET student_name = ?, student_nickname = ?, parent_name = ?, parent_car_plate = ?, parent_phone = ? WHERE id = ?");
                $stmt->execute([$student_name, $student_nickname, $parent_name, $parent_car_plate, $parent_phone, $student_id]);
                
                $success = "แก้ไขข้อมูลนักเรียนเรียบร้อยแล้ว!";
                
                // ดึงข้อมูลใหม่หลังจากอัพเดท
                $stmt = $pdo->prepare("SELECT * FROM students WHERE id = ?");
                $stmt->execute([$student_id]);
                $student = $stmt->fetch();
            }
            
        } catch(PDOException $e) {
            $error = "เกิดข้อผิดพลาดในการแก้ไขข้อมูล: " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>แก้ไขข้อมูลนักเรียน - ระบบจัดการข้อมูลนักเรียน</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header-section">
            <h1><i class="fas fa-user-edit me-3"></i>แก้ไขข้อมูลนักเรียน</h1>
        </div>

        <!-- Content -->
        <div class="content-wrapper">
            <!-- Navigation -->
            <div class="control-panel">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h4 class="mb-0">
                            <i class="fas fa-edit me-2"></i>
                            <?php if ($student): ?>
                                แก้ไขข้อมูล: <?php echo htmlspecialchars($student['student_name']); ?>
                            <?php else: ?>
                                แก้ไขข้อมูลนักเรียน
                            <?php endif; ?>
                        </h4>
                    </div>
                    <div class="col-md-6 text-end">
                        <a href="index.php" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าหลัก
                        </a>
                    </div>
                </div>
            </div>

            <!-- Alert Messages -->
            <?php if ($success): ?>
                <div class="alert alert-success-custom">
                    <i class="fas fa-check-circle me-2"></i><?php echo $success; ?>
                </div>
            <?php endif; ?>

            <?php if ($error): ?>
                <div class="alert alert-danger-custom">
                    <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
                </div>
            <?php endif; ?>

            <?php if ($student): ?>
                <!-- Edit Form -->
                <div class="form-container">
                    <form method="POST" id="studentForm">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label-custom">
                                    <i class="fas fa-user me-2"></i>ชื่อนักเรียน <span class="text-danger">*</span>
                                </label>
                                <input type="text" 
                                       name="student_name" 
                                       id="student_name"
                                       class="form-control form-control-custom" 
                                       placeholder="กรอกชื่อนักเรียน"
                                       value="<?php echo htmlspecialchars($student['student_name']); ?>"
                                       required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label-custom">
                                    <i class="fas fa-smile me-2"></i>ชื่อเล่น <span class="text-danger">*</span>
                                </label>
                                <input type="text" 
                                       name="student_nickname" 
                                       id="student_nickname"
                                       class="form-control form-control-custom" 
                                       placeholder="กรอกชื่อเล่น"
                                       value="<?php echo htmlspecialchars($student['student_nickname']); ?>"
                                       required>
                                <div class="form-text text-muted">
                                    <i class="fas fa-info-circle me-1"></i>ชื่อเล่นต้องไม่ซ้ำกับนักเรียนคนอื่น
                                </div>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label-custom">
                                    <i class="fas fa-user-tie me-2"></i>ชื่อผู้ปกครอง <span class="text-danger">*</span>
                                </label>
                                <input type="text" 
                                       name="parent_name" 
                                       id="parent_name"
                                       class="form-control form-control-custom" 
                                       placeholder="กรอกชื่อผู้ปกครอง"
                                       value="<?php echo htmlspecialchars($student['parent_name']); ?>"
                                       required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label-custom">
                                    <i class="fas fa-car me-2"></i>ทะเบียนรถ<span class="text-danger">*</span>
                                </label>
                                <input type="text" 
                                       name="parent_car_plate" 
                                       class="form-control form-control-custom" 
                                       placeholder="กรอกทะเบียนรถ"
                                       value="<?php echo htmlspecialchars($student['parent_car_plate']); ?>">
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label-custom">
                                    <i class="fas fa-phone me-2"></i>เบอร์โทรศัพท์<span class="text-danger">*</span>
                                </label>
                                <input type="tel" 
                                       name="parent_phone" 
                                       class="form-control form-control-custom" 
                                       placeholder="กรอกเบอร์โทรศัพท์"
                                       value="<?php echo htmlspecialchars($student['parent_phone']); ?>">
                            </div>
                            <div class="col-md-6 d-flex align-items-end">
                                <small class="text-muted">
                                    <i class="fas fa-info-circle me-2"></i>
                                    ฟิลด์ที่มีเครื่องหมาย <span class="text-danger">*</span> จำเป็นต้องกรอก
                                </small>
                            </div>
                        </div>

                        <div class="row mt-4">
                            <div class="col-12 text-center">
                                <button type="submit" class="btn btn-success-custom btn-lg me-3">
                                    <i class="fas fa-save me-2"></i>บันทึกการแก้ไข
                                </button>
                                <a href="index.php" class="btn btn-secondary btn-lg">
                                    <i class="fas fa-times me-2"></i>ยกเลิก
                                </a>
                            </div>
                        </div>
                    </form>
                </div>

                <!-- Student Info Card -->
                <div class="mt-4">
                    <div class="alert" style="background: rgba(90, 103, 216, 0.2); color: #90cdf4; border-left: 4px solid var(--accent-blue);">
                        <h6><i class="fas fa-info-circle me-2"></i>ข้อมูลเดิม</h6>
                        <div class="row">
                            <div class="col-md-4">
                                <strong>ชื่อนักเรียน:</strong> <?php echo htmlspecialchars($student['student_name']); ?>
                            </div>
                            <div class="col-md-4">
                                <strong>ชื่อเล่น:</strong> <?php echo htmlspecialchars($student['student_nickname']); ?>
                            </div>
                            <div class="col-md-4">
                                <strong>ผู้ปกครอง:</strong> <?php echo htmlspecialchars($student['parent_name']); ?>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-4">
                                <strong>ทะเบียนรถ:</strong> <?php echo $student['parent_car_plate'] ? htmlspecialchars($student['parent_car_plate']) : '-'; ?>
                            </div>
                            <div class="col-md-4">
                                <strong>เบอร์โทร:</strong> <?php echo $student['parent_phone'] ? htmlspecialchars($student['parent_phone']) : '-'; ?>
                            </div>
                            <div class="col-md-4">
                                <strong>ID:</strong> #<?php echo $student['id']; ?>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Warning Info -->
                <div class="mt-3">
                    <div class="alert alert-warning" style="background: rgba(255, 193, 7, 0.2); color: #fbbf24; border-left: 4px solid #f59e0b;">
                        <h6><i class="fas fa-exclamation-circle me-2"></i>ข้อควรระวัง</h6>
                        <ul class="mb-0">
                            <li>หากเปลี่ยนชื่อเล่น ต้องแน่ใจว่าไม่ซ้ำกับนักเรียนคนอื่น</li>
                            <li>ตรวจสอบข้อมูลให้ถูกต้องก่อนกดบันทึก</li>
                        </ul>
                    </div>
                </div>
            <?php else: ?>
                <!-- No Student Found -->
                <div class="text-center py-5">
                    <i class="fas fa-user-slash fa-5x text-muted mb-4"></i>
                    <h4>ไม่พบข้อมูลนักเรียน</h4>
                    <p class="text-muted">ไม่สามารถค้นหาข้อมูลนักเรียนที่ต้องการแก้ไขได้</p>
                    <a href="index.php" class="btn btn-primary mt-3">
                        <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าหลัก
                    </a>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>