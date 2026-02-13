let $form = $('#register-form');
$form.on('submit', function (e) { 
    e.preventDefault(); // 阻止表单默认提交行为


    let username = $form.find('[name="username"]').val();
    let password = $form.find('[name="password"]').val();
    let cpassword = $form.find('[name="cpassword"]').val();
    let email = $form.find('[name="email"]').val();


    if (!username || !password || !cpassword || !email) {
        alert('请填写所有字段！');
        return;
    }

    if (password !== cpassword) {
        alert('两次输入的密码不一致！');
        return;
    }


    let formData = {
        username: username,
        password: password,
        email: email
    };

    $.post('/register', formData)
        .then(() => { // 注册成功时执行
            console.log('success');
            location.reload(); 
        })
        .catch(() => { // 注册失败时执行
            console.log('error');
        });
});

