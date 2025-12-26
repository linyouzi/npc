// 平滑滾動效果
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// 導航欄滾動效果
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.2)';
    }
    
    lastScroll = currentScroll;
});

// 人格卡片點擊效果
document.querySelectorAll('.personality-card').forEach(card => {
    card.addEventListener('click', function() {
        const personality = this.dataset.personality;
        
        // 移除其他卡片的選中狀態
        document.querySelectorAll('.personality-card').forEach(c => {
            c.style.transform = '';
            c.style.boxShadow = '';
        });
        
        // 添加選中效果
        this.style.transform = 'scale(1.05)';
        this.style.boxShadow = '0 20px 25px -5px rgba(99, 102, 241, 0.3)';
        
        // 顯示提示（可選）
        console.log(`已選擇人格：${personality}`);
    });
});

// 滾動時的元素動畫
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// 觀察所有卡片元素
document.querySelectorAll('.feature-card, .app-card, .personality-card, .arch-box').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// 響應式導航欄
const navLinks = document.querySelector('.nav-links');
const navbarContainer = document.querySelector('.navbar .container');

// 在移動設備上添加漢堡選單（可選功能）
if (window.innerWidth <= 768) {
    // 可以添加漢堡選單的邏輯
}

