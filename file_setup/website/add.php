<?php
// add.php - หน้าเพิ่มข้อมูลนักเรียน
require_once 'config.php';

$success = '';
$error = '';

// ประมวลผลฟอร์มเมื่อมีการส่งข้อมูล
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
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
            // ตรวจสอบชื่อเล่นซ้ำ
            $stmt = $pdo->prepare("SELECT id FROM students WHERE student_nickname = ? AND status = 1");
            $stmt->execute([$student_nickname]);
            $existing_student = $stmt->fetch();
            
            if ($existing_student) {
                $error = "ชื่อเล่น \"" . htmlspecialchars($student_nickname) . "\" มีอยู่แล้ว กรุณาใช้ชื่อเล่นอื่น";
            } else {
                // เพิ่มข้อมูลลงฐานข้อมูล
                $stmt = $pdo->prepare("INSERT INTO students (student_name, student_nickname, parent_name, parent_car_plate, parent_phone) VALUES (?, ?, ?, ?, ?)");
                $stmt->execute([$student_name, $student_nickname, $parent_name, $parent_car_plate, $parent_phone]);
                
                $success = "เพิ่มข้อมูลนักเรียนเรียบร้อยแล้ว!";
                
                // ล้างข้อมูลในฟอร์ม
                $_POST = array();
            }
            
        } catch(PDOException $e) {
            $error = "เกิดข้อผิดพลาดในการเพิ่มข้อมูล: " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เพิ่มข้อมูลนักเรียน - ระบบจัดการข้อมูลนักเรียน</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header-section">
            <h1><i class="fas fa-user-plus me-3"></i>เพิ่มข้อมูลนักเรียนใหม่</h1>
        </div>

        <!-- Content -->
        <div class="content-wrapper">
            <!-- Navigation -->
            <div class="control-panel">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h4 class="mb-0"><i class="fas fa-plus-circle me-2"></i>ฟอร์มเพิ่มข้อมูล</h4>
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

            <!-- Add Form -->
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
                                   value="<?php echo isset($_POST['student_name']) ? htmlspecialchars($_POST['student_name']) : ''; ?>"
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
                                   value="<?php echo isset($_POST['student_nickname']) ? htmlspecialchars($_POST['student_nickname']) : ''; ?>"
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
                                   value="<?php echo isset($_POST['parent_name']) ? htmlspecialchars($_POST['parent_name']) : ''; ?>"
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
                                   value="<?php echo isset($_POST['parent_car_plate']) ? htmlspecialchars($_POST['parent_car_plate']) : ''; ?>">
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
                                   value="<?php echo isset($_POST['parent_phone']) ? htmlspecialchars($_POST['parent_phone']) : ''; ?>">
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
                                <i class="fas fa-save me-2"></i>บันทึกข้อมูล
                            </button>
                            <button type="button" class="btn btn-secondary btn-lg" onclick="clearForm()">
                                <i class="fas fa-eraser me-2"></i>ล้างข้อมูล
                            </button>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Information -->
            <div class="mt-4">
                <div class="alert alert-info" style="background: rgba(90, 103, 216, 0.2); color: #90cdf4; border-left: 4px solid var(--accent-blue);">
                    <h6><i class="fas fa-lightbulb me-2"></i>คำแนะนำ</h6>
                    <ul class="mb-0">
                        <li>กรอกข้อมูลให้ครบถ้วนและถูกต้อง</li>
                        <li><strong>ชื่อเล่นไม่สามารถซ้ำได้</strong> หากชื่อเล่นซ้ำโปรดตั้งชื่อเล่นใหม่ เช่น วุ้น -> วุ้นเส้น</li>
                        <li>ตรวจสอบข้อมูลก่อนกดบันทึก</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>