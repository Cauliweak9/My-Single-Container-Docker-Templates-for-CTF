document.addEventListener('DOMContentLoaded', function () {
    // 为门添加点击效果
    const doors = document.querySelectorAll('.door-card');

    doors.forEach(door => {
        door.addEventListener('click', function (e) {
            if (!this.classList.contains('door-visited') && !this.classList.contains('special-door')) {
                // 添加点击动画
                this.classList.add('animate__animated', 'animate__pulse');

                // 动画结束后移除类
                this.addEventListener('animationend', function () {
                    this.classList.remove('animate__animated', 'animate__pulse');
                }, { once: true });
            }
        });
    });

    // 主题切换按钮
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-sm btn-outline-secondary position-fixed bottom-0 end-0 m-3';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.title = '切换主题';
    document.body.appendChild(themeToggle);

    themeToggle.addEventListener('click', function () {
        const html = document.documentElement;
        const isDark = html.getAttribute('data-bs-theme') === 'dark';

        html.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
        this.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    // 进度条动画
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        setTimeout(() => {
            progressBar.style.transition = 'width 1s ease';
        }, 500);
    }
});