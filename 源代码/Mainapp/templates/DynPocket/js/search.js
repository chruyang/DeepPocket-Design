// function checkSearchInput() {
//     event.preventDefault(); // 阻止表单的默认提交行为
//     var searchInput = document.getElementById("searchInput").value.trim();
//     console.log("asd")
//     if (!searchInput) {
//         displayAlert("Warning: Please enter search content!");
//     } else {
//         // 如果输入有效，则继续进行搜索操作
//         search();
//     }
// }

function search() {
    var selectedOption = document.getElementById("selectBox").value;
    var searchContent = document.getElementById("searchInput").value;
    $.get("http://localhost:8000/searchPDB?"+selectedOption+"="+searchContent,{},function(data){
			console.log(data);
            var responseData = JSON.parse(data);
            document.getElementById("PDBID").innerText = responseData.PDBID;
            document.getElementById("UniPortID").innerText = responseData.UniPortID;
            document.getElementById("Sequence").innerText = responseData.Sequence;
            document.getElementById("Description").innerText = responseData.Description;
            document.getElementById('structure_image').src = 'http://localhost:8000/searchPDB_searchimg';
            document.getElementById("download_link").href = responseData.download_link;
		});
    // xhr.onreadystatechange = function () {
    //     if (xhr.readyState === 4 && xhr.status === 200) {
    //
    //         var responseData = JSON.parse(xhr.responseText);
    //         // alert(responseData)
    //         // 渲染
    //         document.getElementById("pdb_id").innerText = responseData.PDBID;
    //         document.getElementById("uniprot_id").innerText = responseData.UniProtID;
    //         document.getElementById("sequence").innerText = responseData.Sequence;
    //         document.getElementById("description").innerText = responseData.Description;
    //         document.getElementById("download_link").href = responseData.download_link;
    //         // document.getElementById("structure_image").src = responseData.image_url;
    //     }
    // };
    // xhr.send(JSON.stringify({selectedOption: "PBDID", searchContent: "ace32"}));

}
function handleFormSubmit(event) {
    event.preventDefault(); // 阻止表单的默认提交行为

    var searchInput = document.getElementById("searchInput").value.trim();
    if (!searchInput) {
        alert("Please enter search content!");
    } else {
        // 如果输入有效，则可以继续进行搜索操作
        search(); // 假设这是您定义的搜索函数
    }
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


