function checkInput() {
    var fileInput = document.getElementById("fileInput");
    var contentInput = document.getElementById("contentInput");

    if (!fileInput.files.length && !contentInput.value.trim()) {
        displayAlert("Warning: Please enter the specification content!");
    } else {
        // 如果输入有效，则继续进行其他操作，例如提交表单或执行其他操作
        // 这里可以调用 predict() 函数来处理提交操作
        predict();
    }
}
function predict() {
    // 在这里添加提交操作的代码
    // 这里只是一个示例，可以根据实际情况进行修改
    window.location.href = 'prediction_output.html'
}
// 显示警告框并设置定时器自动隐藏
function displayAlert(message) {
    var alertDiv = document.createElement("div");
    alertDiv.classList.add("alert");

    var alertMessage = document.createElement("div");
    alertMessage.classList.add("alert-message");
    alertMessage.innerText = message;

    alertDiv.appendChild(alertMessage);
    document.body.appendChild(alertDiv);

    // 3秒后自动隐藏警告框
    setTimeout(function() {
        alertDiv.style.display = "none";
    }, 1500);
}