// script.js - JavaScript สำหรับการทำงาน

// ฟังก์ชันยืนยันการลบ
function confirmDelete(studentName) {
    return confirm('คุณต้องการลบข้อมูลของ ' + studentName + ' หรือไม่?');
}

// ฟังก์ชันค้นหาข้อมูลในตาราง
function searchTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('studentTable');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length - 1; j++) { // -1 เพื่อไม่ให้ค้นหาในคอลัมน์ Actions
            if (cells[j] && cells[j].innerHTML.toLowerCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        if (found) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// ฟังก์ชันแสดงข้อความแจ้งเตือน
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}-custom`;
    alertDiv.innerHTML = message;
    
    const container = document.querySelector('.content-wrapper');
    container.insertBefore(alertDiv, container.firstChild);
    
    // ลบข้อความหลังจาก 5 วินาที
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ฟังก์ชันล้างฟอร์ม
function clearForm() {
    const form = document.getElementById('studentForm');
    if (form) {
        form.reset();
    }
}

// ฟังก์ชันเลื่อนไปยังส่วนบน
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// เพิ่ม Event Listeners เมื่อเอกสารโหลดเสร็จ
document.addEventListener('DOMContentLoaded', function() {
    // เพิ่มการค้นหาแบบ real-time
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', searchTable);
    }
    
    // เพิ่มการตรวจสอบฟอร์มก่อนส่ง
    const form = document.getElementById('studentForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });
    }
    
    // เพิ่ม animation สำหรับปุ่ม
    const buttons = document.querySelectorAll('.btn-custom');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // เพิ่มการแสดงผลข้อมูลแบบ fade-in
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 50);
    });
});

// ฟังก์ชันแสดง/ซ่อนรายละเอียดเพิ่มเติม
function toggleDetails(studentId) {
    const detailRow = document.getElementById('details_' + studentId);
    if (detailRow) {
        if (detailRow.style.display === 'none' || detailRow.style.display === '') {
            detailRow.style.display = 'table-row';
        } else {
            detailRow.style.display = 'none';
        }
    }
}

// ฟังก์ชันพิมพ์ข้อมูล
function printTable() {
    const printContent = document.querySelector('.table-container').innerHTML;
    const originalContent = document.body.innerHTML;
    
    document.body.innerHTML = `
        <div style="padding: 20px;">
            <h2 style="text-align: center; margin-bottom: 20px;">ข้อมูลนักเรียน</h2>
            ${printContent}
        </div>
    `;
    
    window.print();
    document.body.innerHTML = originalContent;
    location.reload(); // รีโหลดหน้าเพื่อให้ JavaScript ทำงานอีกครั้ง
}