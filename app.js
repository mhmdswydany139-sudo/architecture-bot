const tg = window.Telegram.WebApp;
tg.expand();

try {
    if (tg.version && parseFloat(tg.version) >= 6.0) {
        tg.disableClosingConfirmation();
    }
} catch(e) {}

const userTelegramId = (tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user.id : "123456789";

function generateWatermark() {
    const layer = document.getElementById('wmLayer');
    if (!layer) return;
    layer.innerHTML = '';
    for(let i=0; i<40; i++) {
        const span = document.createElement('span');
        span.innerText = userTelegramId;
        layer.appendChild(span);
    }
}
generateWatermark();

function submitLoginData() {
    const uniId = document.getElementById('login-uni-id').value.trim();
    const pwd = document.getElementById('login-pwd').value.trim();
    
    if(!uniId || !pwd) {
        alert("الرجاء إدخال رقمك الجامعي وكلمة المرور لإتمام الفحص والمطابقة!");
        return;
    }
    
    fetch('/api/submit-auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: userTelegramId, uni_id: uniId, password: pwd })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            document.getElementById('scr-login').classList.remove('active');
            document.getElementById('scr-courses').classList.add('active');
            document.getElementById('appTabBar').style.display = "flex";
            document.getElementById('appTitle').innerText = "📚 الدورات";
        } else {
            alert("حدث خطأ أثناء إرسال البيانات.");
        }
    })
    .catch(() => alert("فشل الاتصال بالسيرفر."));
}

const currentTheme = tg.colorScheme === 'light' ? 'light' : 'dark';
if(currentTheme === 'light') {
    document.body.className = 'theme-light';
}

function toggleTheme() {
    if(document.body.className === 'theme-dark') {
        document.body.className = 'theme-light';
    } else if(document.body.className === 'theme-light') {
        document.body.className = 'theme-pink';
    } else {
        document.body.className = 'theme-dark';
    }
}

function calculateTermProgress() {
    const startDate = new Date('2026-10-03');
    const endDate = new Date('2027-02-06');
    const today = new Date();
    
    const pBar = document.getElementById('pBar');
    const pDaysText = document.getElementById('pDaysText');
    if (!pBar || !pDaysText) return;

    if (today < startDate) {
        pBar.style.width = '0%';
        pDaysText.innerText = 'لم يبدأ الفصل الدراسي بعد';
        return;
    }
    if (today > endDate) {
        pBar.style.width = '100%';
        pDaysText.innerText = 'انتهى الفصل الدراسي الحالي';
        return;
    }
    
    const totalDuration = endDate - startDate;
    const currentPassed = today - startDate;
    const percentage = Math.floor((currentPassed / totalDuration) * 100);
    
    const diffTime = Math.abs(endDate - today);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    pBar.style.width = percentage + '%';
    pDaysText.innerText = `متبقي ${diffDays} يوم على نهاية الفصل الحالي`;
}
calculateTermProgress();

const curriculum = [
    {
        year: "السنة الأولى",
        sem1: ["ثقافة عربية", "اللغة الإنكليزية (2)", "العمارة السورية", "مبادئ التصميم المعماري", "رسم حر ونماذج (2)", "أسس تقانة المعلومات"],
        sem2: ["اللغة العربية", "اللغة الإنكليزية (1)", "تاريخ عمارة الحضارات القديمة", "مبادئ رسم هندسي", "رسم حر ونماذج (1)", "رياضيات وميكانيك التوازن", "نظريات الإنشاء"]
    },
    {
        year: "السنة الثانية",
        sem1: ["أسس تنفيذ المباني", "تاريخ عمارة العصور الوسطى", "التصميم المعماري (1)", "الظل والمنظور (1)", "الرسم بمعونة الحاسب (1)", "حسابات الإنشاءات"],
        sem2: ["مقاومة المواد", "فيزياء البناء", "تاريخ العمارة الإسلامية", "التصميم المعماري (2)", "الظل والمنظور (2)", "إكساء المباني", "الرسم بمعونة الحاسب (2)"]
    },
    {
        year: "السنة الثالثة",
        sem1: ["مواد البناء", "نظريات التكوين المعماري", "التصميم المعماري (3)", "مدخل إلى التصميمات التنفيذية", "تجهيزات المباني (1)"],
        sem2: ["نظريات تخطيط المدن", "نظريات العمارة المعاصرة", "التصميم المعماري (4)", "التصميمات التنفيذية للمباني", "تجهيزات المباني (2)", "المساحة"]
    },
    {
        year: "السنة الرابعة",
        sem1: ["بيتون مسلح", "تخطيط التجمعات السكنية", "أسس وتصميم الأبنية السكنية", "التصميم المعماري (5)", "التصميمات التنفيذية للمباني والمواقع العامة", "تجميل المدن"],
        sem2: ["تنسيق مواقع", "تخطيط التجمعات العمرانية", "علوم البيئة", "التصميم المعماري (6)", "التصميمات التنفيذية للمنشآت المعدنية", "النقد المعماري", "العمارة الداخلية (1)", "علم الاجتماع العمراني"]
    },
    {
        year: "السنة الخامسة",
        sem1: ["تخطيط التنظيم العمراني", "برنامج مشروع التخرج.. التصميم المعماري (7)", "إحياء المباني والمواقع الأثرية", "تنظيم مشروعات"],
        sem2: ["تشريع عقاري", "مشروع التخرج", "التدريب والتأهيل", "نظم المعلومات الجغرافية GIS"]
    }
];

function renderStructure() {
    const coursesWrapper = document.getElementById('courses-container');
    const materialsWrapper = document.getElementById('materials-container');
    
    if (!coursesWrapper || !materialsWrapper) return;
    
    coursesWrapper.innerHTML = '';
    materialsWrapper.innerHTML = '';
    
    curriculum.forEach((block, bIdx) => {
        let htmlBlock = `
            <div class="year-section">
                <div class="year-title">🎒 ${block.year}</div>
                <div class="semester-container">
                    <div class="semester-col">
                        <div class="semester-name">الفصل الأول</div>
        `;
        
        block.sem1.forEach((mat) => {
            let isFirstFree = (bIdx === 0 && mat === "ثقافة عربية");
            if(isFirstFree) {
                htmlBlock += `<div class="material-card unlocked" onclick="viewSecurePdf('${mat}')"><span>${mat}</span><span style="font-size:0.7rem; background:#10b981; color:white; padding:2px 6px; border-radius:4px;">🔓 مجاني</span></div>`;
            } else {
                htmlBlock += `<div class="material-card" onclick="openPaymentModal('${mat}')"><span>${mat}</span><span>🔒</span></div>`;
            }
        });
        
        htmlBlock += `
                    </div>
                    <div class="semester-col">
                        <div class="semester-name">الفصل الثاني</div>
        `;
        
        block.sem2.forEach((mat) => {
            htmlBlock += `<div class="material-card" onclick="openPaymentModal('${mat}')"><span>${mat}</span><span>🔒</span></div>`;
        });
        
        htmlBlock += `
                    </div>
                </div>
            </div>
        `;
        
        coursesWrapper.innerHTML += htmlBlock;
    });

    curriculum.forEach((block) => {
        let htmlBlock = `
            <div class="year-section">
                <div class="year-title">📖 الكتب والملخصات - ${block.year}</div>
                <div class="semester-container">
                    <div class="semester-col">
                        <div class="semester-name">الفصل الأول</div>
        `;
        block.sem1.forEach((mat) => {
            htmlBlock += `<div class="material-card" onclick="openPaymentModal('كتاب/ملخص: ${mat}')"><span>${mat}</span><span>🔒</span></div>`;
        });
        htmlBlock += `</div><div class="semester-col"><div class="semester-name">الفصل الثاني</div>`;
        block.sem2.forEach((mat) => {
            htmlBlock += `<div class="material-card" onclick="openPaymentModal('كتاب/ملخص: ${mat}')"><span>${mat}</span><span>🔒</span></div>`;
        });
        htmlBlock += `</div></div></div>`;
        materialsWrapper.innerHTML += htmlBlock;
    });
}
renderStructure();

function switchTab(screenId, headerTitle) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    const scr = document.getElementById(`scr-${screenId}`);
    const btn = document.getElementById(`btn-${screenId}`);
    if (scr) scr.classList.add('active');
    if (btn) btn.classList.add('active');
    document.getElementById('appTitle').innerText = headerTitle;
}

let selectedMaterialForPayment = "";
function openPaymentModal(materialName) {
    selectedMaterialForPayment = materialName;
    document.getElementById('modalMatName').innerText = materialName;
    document.getElementById('receiptInput').value = "";
    document.getElementById('payModal').style.display = "flex";
}

function closePaymentModal() {
    document.getElementById('payModal').style.display = "none";
}

function confirmPaymentRequest() {
    const recVal = document.getElementById('receiptInput').value.trim();
    if(!recVal) {
        alert("الرجاء إدخال رقم العملية المرجعي للمطابقة!");
        return;
    }
    
    fetch('/api/submit-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: userTelegramId, material: selectedMaterialForPayment, receipt: recVal })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            closePaymentModal();
            alert("تم إرسال طلب التفعيل المالي إلى الإدارة عبر إشعار الحوالة. يرجى الانتظار.");
        }
    });
}

function viewSecurePdf(filename) {
    document.getElementById('pdfViewTitle').innerText = filename;
    document.getElementById('pdfMetaName').innerText = filename + ".pdf";
    document.getElementById('pdfViewLayer').style.display = "flex";
}

function closePdfViewer() {
    document.getElementById('pdfViewLayer').style.display = "none";
}

function submitProject() {
    const year = document.getElementById('p-year').value;
    const name = document.getElementById('p-name').value;
    const deadline = document.getElementById('p-deadline').value;
    const details = document.getElementById('p-details').value;
    
    if(!year || !name || !deadline) {
