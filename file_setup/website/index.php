<?php
// index.php - หน้าแสดงรายการนักเรียน
require_once 'config.php';

// ดึงข้อมูลนักเรียนทั้งหมดที่ยังไม่ถูกลบ
try {
    $stmt = $pdo->prepare("SELECT * FROM students WHERE status = 1 ORDER BY id DESC");
    $stmt->execute();
    $students = $stmt->fetchAll();
} catch(PDOException $e) {
    $error = "เกิดข้อผิดพลาด: " . $e->getMessage();
}
?>

<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบจัดการข้อมูลนักเรียน</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="style.css" rel="stylesheet">
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <div class="header-section">
            <h1><i class="fas fa-graduation-cap me-3"></i>ระบบจัดการข้อมูลนักเรียน</h1>
        </div>

        <!-- Content -->
        <div class="content-wrapper">
            <?php if (isset($error)): ?>
                <div class="alert alert-danger-custom">
                    <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
                </div>
            <?php endif; ?>

            <!-- Control Panel -->
            <div class="control-panel">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h4 class="mb-0"><i class="fas fa-users me-2"></i>จัดการข้อมูลนักเรียน</h4>
                    </div>
                    <div class="col-md-6 text-end">
                        <a href="add.php" class="btn btn-success-custom">
                            <i class="fas fa-plus me-2"></i>เพิ่มนักเรียนใหม่
                        </a>
                        <button onclick="printTable()" class="btn btn-info">
                            <i class="fas fa-print me-2"></i>พิมพ์
                        </button>
                    </div>
                </div>
            </div>

            <!-- Search -->
            <div class="search-container">
                <div class="row">
                    <div class="col-md-6">
                        <label class="form-label-custom">ค้นหาข้อมูล</label>
                        <input type="text" id="searchInput" class="search-input" placeholder="ค้นหาชื่อ, ชื่อเล่น, ผู้ปกครอง...">
                    </div>
                    <div class="col-md-6 d-flex align-items-end">
                        <span class="text-muted">
                            <i class="fas fa-info-circle me-2"></i>
                            พบข้อมูลทั้งหมด <?php echo count($students); ?> รายการ
                        </span>
                    </div>
                </div>
            </div>

            <!-- Students Table -->
            <div class="table-container">
                <table class="table table-dark-custom" id="studentTable">
                    <thead>
                        <tr>
                            <th style="width: 4%">#</th>
                            <th style="width: 15%">ชื่อนักเรียน</th>
                            <th style="width: 12%">ชื่อเล่น</th>
                            <th style="width: 15%">ชื่อผู้ปกครอง</th>
                            <th style="width: 25%">ทะเบียนรถผู้ปกครอง</th>
                            <th style="width: 12%">เบอร์โทร</th>
                            <th style="width: 8%">สถานะ</th>
                            <th style="width: 10%">การจัดการ</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (empty($students)): ?>
                            <tr>
                                <td colspan="8" class="text-center py-4">
                                    <i class="fas fa-user-slash fa-3x mb-3 text-muted"></i>
                                    <p class="mb-0">ไม่มีข้อมูลนักเรียน</p>
                                </td>
                            </tr>
                        <?php else: ?>
                            <?php $counter = 1; ?>
                            <?php foreach ($students as $student): ?>
                                <tr>
                                    <td><?php echo $counter++; ?></td>
                                    <td>
                                        <i class="fas fa-user me-2"></i>
                                        <?php echo htmlspecialchars($student['student_name']); ?>
                                    </td>
                                    <td><?php echo htmlspecialchars($student['student_nickname']); ?></td>
                                    <td>
                                        <i class="fas fa-user-tie me-2"></i>
                                        <?php echo htmlspecialchars($student['parent_name']); ?>
                                    </td>
                                    <td>
                                        <?php if ($student['parent_car_plate']): ?>
                                            <i class="fas fa-car me-2"></i>
                                            <?php echo htmlspecialchars($student['parent_car_plate']); ?>
                                        <?php else: ?>
                                            <span class="text-muted">-</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <?php if ($student['parent_phone']): ?>
                                            <i class="fas fa-phone me-2"></i>
                                            <?php echo htmlspecialchars($student['parent_phone']); ?>
                                        <?php else: ?>
                                            <span class="text-muted">-</span>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <span class="status-active">
                                            <i class="fas fa-check-circle me-1"></i>ใช้งาน
                                        </span>
                                    </td>
                                    <td>
                                        <div class="action-buttons">
                                            <a href="edit.php?id=<?php echo $student['id']; ?>" 
                                               class="btn btn-warning-custom btn-sm" 
                                               title="แก้ไข">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                            <a href="delete.php?id=<?php echo $student['id']; ?>" 
                                               class="btn btn-danger-custom btn-sm" 
                                               title="ลบ"
                                               onclick="return confirmDelete('<?php echo htmlspecialchars($student['student_name']); ?>')">
                                                <i class="fas fa-trash"></i>
                                            </a>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>

            <!-- Footer Info -->
            <div class="mt-4 text-center">
                <p class="text-muted mb-0">
                    <i class="fas fa-info-circle me-2"></i>
                    ระบบจัดการข้อมูลนักเรียน-Student Name Announcement System Based on Parent License Plates
                </p>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>