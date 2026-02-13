$('#loginForm').on('submit', (e) => {
    e.preventDefault();
    let hash = {};
    let arg = ['email', 'password'];
    arg.forEach((name) => {
        let value = $('#loginForm').find(`[name= ${name}]`).val();
        hash[name] = value;
    })
    $('#loginForm').find('.error').each((index, span) => {
        $(span).text('');
    })


    // if(hash['email'] === ''){
    //     $('#loginForm').find('[name = "email"]').siblings('.error').text('请输入邮箱');
    //     return
    // }
    // if(hash['password'] === ''){
    //     $('#loginForm').find('[name = "password"]').siblings('.error').text('请输入密码');
    //     return
    // }





    //ajax发送post请求
    $.post('/login', hash).then(() => { window.location.href = "/" },
        () => {
            alert("Login failed, please try again")
            // ShowFailure(" Login failed, please try again ")
        })
})