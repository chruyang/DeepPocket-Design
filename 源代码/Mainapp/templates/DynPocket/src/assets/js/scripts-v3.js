// 版权声明和许可信息
// 这段代码是由 Microsoft Corporation 发布的，根据 MIT 许可证授权。

var stage; // 定义全局变量 stage

// 当选择文件按钮被点击时触发的事件处理程序
$('#btnSelectFiles').on('click', function () {
	$('#files').trigger('click'); // 触发 input[type=file] 的点击事件
});

// 当文件选择框内容改变时触发的事件处理程序
$("#files").change(function () {
	let filename = $("#files").val().split('\\').pop(); // 获取文件名
	if (filename == "") {
		$('#btnSelectFiles').html("Choose file"); // 若未选择文件，显示 "Choose file"
	} else {
		$('#btnSelectFiles').html(filename); // 若选择了文件，显示文件名
	}
});

// 当下载按钮被点击时触发的事件处理程序
$('#Download').on('click', function () {
	saveAs(downloadFile); // 下载文件
});

// 当清空按钮被点击时触发的事件处理程序
$('#btnClear').on('click', function () {
	restartForm(); // 重置表单
});

// 当文件选择框内容改变时触发的事件处理程序
$('#files').on('change', function () {
	$("#fileUploadSelectedFiles").empty(); // 清空已选择文件列表
	for (var i = 0; i < $(this).get(0).files.length; ++i) {
		var silgleFile = $(this).get(0).files[i].name.replace(/C:\\fakepath\\/i, ''); // 获取文件名
		$("#fileUploadSelectedFiles").append('<div class="labelFileUploadSectionC">' + silgleFile + '</div>'); // 将文件名显示在界面上
	}
});

let loadingFlag; // 定义加载标志变量
$(document).ready(function () {
	var isFile = false;
	$(document).ajaxComplete(function () {
	});

	// 当提交按钮被点击时触发的事件处理程序
	$('#btnSubmit').click(function () {
		loadingFlag = false; // 加载标志置为 false
		let filename = $('#btnSelectFiles').html(); // 获取文件名
		if (filename == "Choose file") {

			$('chkTermsAndConditions').prop('disabled', true); // 禁用复选框
			$(".preloader").show(); // 显示加载动画


			var selectedOption = document.getElementById("selectBox").value;
			var searchContent = document.getElementById("contentInput").value;
			$.get("http://http://8.218.164.134:8000/prediction_out/?" + selectedOption + "=" + encodeURIComponent(searchContent), function (response) {
				console.log(response);
				// var responseData = JSON.parse(data);
				processReponse(response); // 处理服务器响应
						isFile = true; // 设置文件标志为 true
						completeForm(); // 完成表单填写
						loadingFlag = true; // 加载标志置为 true
			}).fail(function (xhr, textStatus, errorThrown) {
				alert('An error occurred: ' + textStatus);
			});

			// alert("Please select a .pdb file"); // 提示用户选择 .pdb 文件
		}
		else {
			$('chkTermsAndConditions').prop('disabled', true); // 禁用复选框
			$(".preloader").show(); // 显示加载动画
			var form_data = new FormData(); // 创建 FormData 对象
			var totalfiles = document.getElementById('files').files.length; // 获取文件数量
			for (var index = 0; index < totalfiles; index++) {
				form_data.append("files[]", document.getElementById('files').files[index]); // 将文件添加到 FormData 中
			}

			$.ajax({
				url: `your model url`, // 请求的 URL
				type: 'post', // 请求类型为 POST
				data: form_data, // 发送的数据
				dataType: 'pdb', // 响应数据类型
				contentType: false, // 不设置 Content-Type
				processData: false, // 不处理数据
				statusCode: {
					500: function () {
						$(".preloader").hide(); // 隐藏加载动画
						restartForm(); // 重置表单
						alert('An error occured while trying to process de PDB file.'); // 提示用户处理文件时发生错误
						loadingFlag = true; // 加载标志置为 true
					},
					415: function (response) {
						$(".preloader").hide(); // 隐藏加载动画
						restartForm(); // 重置表单
						alert(response.responseText); // 提示用户服务器返回的错误信息
						loadingFlag = true; // 加载标志置为 true
					},
					200: function (response) {
						processReponse(response.responseText); // 处理服务器响应
						isFile = true; // 设置文件标志为 true
						completeForm(); // 完成表单填写
						loadingFlag = true; // 加载标志置为 true
					}
				}
			});

		}
	});
});


// 当窗口大小改变时触发的事件处理程序
window.addEventListener("resize", function (event) {
	if (loadingFlag) {
		stage.handleResize(); // 调整舞台大小
	}
}, false);


let linesArray;
// 处理服务器响应的函数









let totLines = [];//开到全局




function processReponse(response) {
	f = chroma.scale(['blue', 'white', 'red']).domain([0, 1]); // 创建颜色映射
	let fileBlob = new Blob([response], {
		type: "text/plain"
	});

	linesArray = response.split("\n"); // 将响应文本按行分割
	downloadFile = new File([fileBlob], "result_model.pdb", { type: "text/plain;charset=utf-8" }); // 创建文件对象

	// let totLines = [];
	for (var i = 0; i < linesArray.length; i++) {
		let currentLine = linesArray[i];
		if (currentLine.substring(0, 4) == "ATOM") {
			let currNumber = currentLine.substring(23, 26).split(' ').join('') + "-" + currentLine.substring(23, 26).split(' ').join('');
			let currValue = currentLine.substring(62, 66).split(' ').join('');
			lines = [f(currValue).hex(), currNumber];
			totLines.push(lines);
		}
	}

	// stage = new NGL.Stage("viewport"); // 创建 NGL 舞台//
	stage = new NGL.Stage("viewport", { backgroundColor: "black" });

	stage.loadFile(downloadFile).then(function (o) {
		var schemeId = NGL.ColormakerRegistry.addSelectionScheme(totLines, 'pocker miner'); // 添加颜色方案
		o.addRepresentation("rocket", { colorScheme: schemeId }); // 添加表示
		o.autoView(); // 自动调整视图
	});

}


///////////////////////////////////////////////////////////////////////////////////////////////////
// 监听下拉框的变化事件

$('select.select-class').change(function () {
	var selectedValue = $(this).val();
	stage.removeAllComponents(); // 移除之前的所有表示

	stage.loadFile(downloadFile).then(function (o) {
		var schemeId = NGL.ColormakerRegistry.addSelectionScheme(totLines, 'pocker miner'); // 添加颜色方案
		o.addRepresentation(selectedValue, { colorScheme: schemeId }); // 添加表示
		o.autoView();
	});
});




















// 完成表单填写的函数
function completeForm() {
	$('#outputpage').show();
	// $('#btnClear').show(); // 显示清空按钮
	$('#inputpage').hide();
	$('#btnDownload').show();

	$('#actionSubtitle').html("Download the file:"); // 修改操作副标题
	$('.scaleContainer').show(); // 显示颜色标尺容器
	$(".preloader").hide(); // 隐藏加载动画
	$('.beforeComplete').hide(); // 隐藏未完成提示

	setchart();//填充图表
	settable();
	stage.handleResize(); // 调整舞台大小
}

// 重置表单的函数
function restartForm() {
	$('chkTermsAndConditions').prop('disabled', false); // 启用复选框
	$('#outputpage').hide();
	// $('#btnClear').hide(); // 隐藏清空按钮
	$('#inputpage').show();


	$('#actionSubtitle').html("Upload a protein PDB file:"); // 修改操作副标题
	$("#files").val(null); // 清空文件输入框
	$("#files").val(''); // 清空文件输入框
	$('#btnSelectFiles').html("Choose file"); // 恢复 "Choose file" 文本
	$('#chkTermsAndConditions').prop('checked', false); // 取消复选框选中状态
	$('#viewport').html(''); // 清空 NGL 舞台
	$('.scaleLabel').hide(); // 隐藏标尺标签
	$('.scaleContainer').hide(); // 隐藏颜色标尺容器
	$('.beforeComplete').show(); // 显示未完成提示
}










$(document).ready(function () {
	$('#outputpage').hide();
	$('#inputpage').show();
	$('#modal-container').hide();


	// $('#outputpage').show();
	// $('#inputpage').hide(); 
	// $('#modal-container').show(); 


});

//
// var refreshbutton = document.getElementById("refreshing");
//
// refreshbutton.addEventListener("click", function () {
// 	if (loadingFlag) {
// 		stage.handleResize(); // 调整舞台大小
// 	}
// });


