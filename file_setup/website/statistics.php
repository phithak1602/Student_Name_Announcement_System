<?php
// config.php - การเชื่อมต่อฐานข้อมูล
$host = 'localhost';
$dbname = 'student_db';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}

// ดึงข้อมูลสำหรับสถิติการมารับนักเรียน
function getPickupStats($pdo) {
    // สถิติรายวัน (7 วันล่าสุด) - เฉพาะที่มีการมารับ
    $dailyStats = $pdo->query("
        SELECT 
            DATE(a.date) as date,
            COUNT(CASE WHEN a.status = 1 THEN 1 END) as picked_up,
            COUNT(*) as total_students
        FROM attendance a
        WHERE a.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(a.date)
        ORDER BY DATE(a.date) DESC
    ")->fetchAll(PDO::FETCH_ASSOC);

    // สถิติรายเดือน - เฉพาะที่มีการมารับ
    $monthlyStats = $pdo->query("
        SELECT 
            MONTH(a.date) as month,
            YEAR(a.date) as year,
            COUNT(CASE WHEN a.status = 1 THEN 1 END) as picked_up,
            COUNT(*) as total_records
        FROM attendance a
        WHERE a.date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY YEAR(a.date), MONTH(a.date)
        ORDER BY YEAR(a.date) DESC, MONTH(a.date) DESC
    ")->fetchAll(PDO::FETCH_ASSOC);

    // สถิติรายนักเรียน - เฉพาะที่ถูกมารับ
    $studentStats = $pdo->query("
        SELECT 
            s.student_name,
            s.student_nickname,
            COUNT(CASE WHEN a.status = 1 THEN 1 END) as pickup_count,
            COUNT(*) as total_days,
            ROUND((COUNT(CASE WHEN a.status = 1 THEN 1 END) / COUNT(*)) * 100, 1) as pickup_rate
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        WHERE s.status = 1 AND a.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY s.id, s.student_name, s.student_nickname
        ORDER BY pickup_rate DESC
    ")->fetchAll(PDO::FETCH_ASSOC);

    // สถิติรวม - เฉพาะการมารับ
    $totalStats = $pdo->query("
        SELECT 
            COUNT(DISTINCT s.id) as total_students,
            COUNT(CASE WHEN a.status = 1 THEN 1 END) as total_pickups,
            COUNT(*) as total_records,
            ROUND((COUNT(CASE WHEN a.status = 1 THEN 1 END) / COUNT(*)) * 100, 1) as pickup_rate
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        WHERE s.status = 1 AND a.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    ")->fetch(PDO::FETCH_ASSOC);

    // สถิติสัดส่วนการมารับ
    $rateStats = [
        ['label' => 'มีการมารับ', 'count' => $totalStats['total_pickups']],
        ['label' => 'ไม่มีการมารับ', 'count' => $totalStats['total_records'] - $totalStats['total_pickups']]
    ];

    return [
        'daily' => $dailyStats,
        'monthly' => $monthlyStats,
        'students' => $studentStats,
        'total' => $totalStats,
        'rate' => $rateStats
    ];
}

$stats = getPickupStats($pdo);
?>

<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>สถิติการมารับนักเรียน</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-bg: #3c4557;
            --card-bg: #4a5568;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --success-color: #48bb78;
            --info-color: #3182ce;
            --warning-color: #ed8936;
        }

        body {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }

        .header-gradient {
            background: var(--primary-gradient);
            padding: 2rem 0;
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: white;
            font-size: 2rem;
            font-weight: bold;
        }

        .stat-card {
            background: var(--card-bg);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .chart-container {
            background: var(--card-bg);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .table-container {
            background: var(--card-bg);
            border-radius: 15px;
            overflow: hidden;
        }

        .table-dark {
            --bs-table-bg: transparent;
        }

        .badge-success {
            background-color: var(--success-color) !important;
        }

        .badge-info {
            background-color: var(--info-color) !important;
        }

        .progress {
            background-color: rgba(255, 255, 255, 0.1);
        }

        .progress-bar {
            background: linear-gradient(90deg, var(--success-color), #68d391);
        }

        .section-title {
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header-gradient">
        <div class="container">
            <h1 class="header-title">
                <i class="fas fa-car"></i>
                สถิติการมารับนักเรียน
            </h1>
        </div>
    </div>

    <div class="container mt-4">
        <!-- สถิติรวม -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number text-info">
                        <?= $stats['total']['total_students'] ?? 0 ?>
                    </div>
                    <div class="stat-label">
                        <i class="fas fa-users"></i> จำนวนนักเรียนทั้งหมด
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number text-success">
                        <?= $stats['total']['total_pickups'] ?? 0 ?>
                    </div>
                    <div class="stat-label">
                        <i class="fas fa-car-side"></i> จำนวนครั้งที่มารับ (30 วัน)
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number text-info">
                        <?= $stats['total']['total_records'] ?? 0 ?>
                    </div>
                    <div class="stat-label">
                        <i class="fas fa-calendar-check"></i> จำนวนวันที่บันทึก
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card text-center">
                    <div class="stat-number text-warning">
                        <?= $stats['total']['pickup_rate'] ?? 0 ?>%
                    </div>
                    <div class="stat-label">
                        <i class="fas fa-percentage"></i> อัตราการมารับโดยรวม
                    </div>
                </div>
            </div>
        </div>

        <!-- กราฟแสดงสถิติรายวัน -->
        <div class="row">
            <div class="col-lg-8">
                <div class="chart-container">
                    <h3 class="section-title">
                        <i class="fas fa-calendar-day"></i>
                        สถิติการมารับ 7 วันล่าสุด
                    </h3>
                    <div style="height: 300px;">
                        <canvas id="dailyChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="chart-container">
                    <h3 class="section-title">
                        <i class="fas fa-pie-chart"></i>
                        สัดส่วนการมารับ
                    </h3>
                    <div style="height: 300px;">
                        <canvas id="rateChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- กราฟแสดงสถิติรายเดือน -->
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <h3 class="section-title">
                        <i class="fas fa-calendar-alt"></i>
                        สถิติการมารับรายเดือน
                    </h3>
                    <div style="height: 250px;">
                        <canvas id="monthlyChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- ตารางสถิติรายนักเรียน -->
        <div class="row">
            <div class="col-12">
                <div class="table-container">
                    <div class="p-3">
                        <h3 class="section-title">
                            <i class="fas fa-user-graduate"></i>
                            สถิติการมารับรายนักเรียน (30 วันล่าสุด)
                        </h3>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-dark table-striped mb-0">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>ชื่อนักเรียน</th>
                                    <th>ชื่อเล่น</th>
                                    <th>จำนวนครั้งที่มารับ</th>
                                    <th>จำนวนวันทั้งหมด</th>
                                    <th>อัตราการมารับ</th>
                                    <th>Progress</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach($stats['students'] as $index => $student): ?>
                                <tr>
                                    <td><?= $index + 1 ?></td>
                                    <td><?= htmlspecialchars($student['student_name']) ?></td>
                                    <td><?= htmlspecialchars($student['student_nickname']) ?></td>
                                    <td>
                                        <span class="badge badge-success">
                                            <?= $student['pickup_count'] ?? 0 ?>
                                        </span>
                                    </td>
                                    <td>
                                        <span class="badge badge-info">
                                            <?= $student['total_days'] ?? 0 ?>
                                        </span>
                                    </td>
                                    <td>
                                        <strong><?= $student['pickup_rate'] ?? 0 ?>%</strong>
                                    </td>
                                    <td>
                                        <div class="progress" style="height: 20px;">
                                            <div class="progress-bar" role="progressbar" 
                                                 style="width: <?= $student['pickup_rate'] ?? 0 ?>%">
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // ข้อมูลสำหรับกราฟ
        const dailyData = <?= json_encode($stats['daily']) ?>;
        const monthlyData = <?= json_encode($stats['monthly']) ?>;
        const rateData = <?= json_encode($stats['rate']) ?>;
        const totalStats = <?= json_encode($stats['total']) ?>;

        // กราฟสถิติรายวัน
        const dailyCtx = document.getElementById('dailyChart').getContext('2d');
        new Chart(dailyCtx, {
            type: 'bar',
            data: {
                labels: dailyData.map(d => {
                    const date = new Date(d.date);
                    return date.toLocaleDateString('th-TH', {
                        month: 'short',
                        day: 'numeric'
                    });
                }).reverse(),
                datasets: [{
                    label: 'จำนวนครั้งที่มารับ',
                    data: dailyData.map(d => d.picked_up).reverse(),
                    backgroundColor: 'rgba(72, 187, 120, 0.8)',
                    borderColor: 'rgba(72, 187, 120, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#a0aec0',
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#a0aec0',
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });

        // กราฟสัดส่วนการมารับ
        const rateCtx = document.getElementById('rateChart').getContext('2d');
        new Chart(rateCtx, {
            type: 'doughnut',
            data: {
                labels: rateData.map(r => r.label),
                datasets: [{
                    data: rateData.map(r => r.count),
                    backgroundColor: [
                        'rgba(72, 187, 120, 0.8)',
                        'rgba(160, 174, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(72, 187, 120, 1)',
                        'rgba(160, 174, 192, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });

        // กราฟรายเดือน
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: monthlyData.map(d => {
                    const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
                                  'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
                    return months[d.month - 1] + ' ' + d.year;
                }).reverse(),
                datasets: [{
                    label: 'จำนวนครั้งที่มารับ',
                    data: monthlyData.map(d => d.picked_up).reverse(),
                    borderColor: 'rgba(72, 187, 120, 1)',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#a0aec0',
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#a0aec0',
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>