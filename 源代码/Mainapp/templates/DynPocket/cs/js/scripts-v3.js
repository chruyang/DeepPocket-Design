// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

var stage;
$('#btnSelectFiles').on('click', function () {
	$('#files').trigger('click');
});

$("#files").change(function () {
	let filename = $("#files").val().split('\\').pop();
	if (filename == "") {
		$('#btnSelectFiles').html("Choose file");
	} else {
		$('#btnSelectFiles').html(filename);
	}
});


$('#btnDownload').on('click', function () {
	saveAs(downloadFile);
});

$('#btnClear').on('click', function () {
	restartForm();
});



$('#files').on('change', function () {
	$("#fileUploadSelectedFiles").empty();
	for (var i = 0; i < $(this).get(0).files.length; ++i) {
		var silgleFile = $(this).get(0).files[i].name.replace(/C:\\fakepath\\/i, '');
		$("#fileUploadSelectedFiles").append('<div class="labelFileUploadSectionC">' + silgleFile + '</div>');
	}

});

let loadingFlag;
$(document).ready(function () {
	var isFile = false;
	$(document).ajaxComplete(function () {
	});

	$('#btnSubmit').click(function () {
		loadingFlag = false;
		let filename = $('#btnSelectFiles').html();
		if (filename == "Choose file") {
			alert("Please select a .pdb file");
		} else {
			$('chkTermsAndConditions').prop('disabled', true);
			$(".preloader").show();
			var form_data = new FormData();
			var totalfiles = document.getElementById('files').files.length;
			for (var index = 0; index < totalfiles; index++) {
				form_data.append("files[]", document.getElementById('files').files[index]);
			}

			$.ajax({
				url: `https://pmin02-api.azurewebsites.net/api/foldingathomeapi`,
				type: 'post',
				data: form_data,
				dataType: 'pdb',
				contentType: false,
				processData: false,
				statusCode: {
					500: function () {
						$(".preloader").hide();
						restartForm();
						alert('An error occured while trying to process de PDB file.');
						loadingFlag = true;
					},
					415: function (response) {
						$(".preloader").hide();
						restartForm();
						alert(response.responseText);
						loadingFlag = true;
					},
					200: function (response) {
						processReponse(response);
						isFile = true;
						completeForm();
						loadingFlag = true;
					}
				}
			});

		}
	});
});


window.addEventListener("resize", function (event) {
	if (loadingFlag) {
		stage.handleResize();
	}
}, false);

function processReponse(response) {
	f = chroma.scale(['blue', 'white', 'red']).domain([0, 1]);
	let fileBlob = new Blob([response.responseText], {
		type: "text/plain"
	});

	let linesArray = response.responseText.split("\n");
	downloadFile = new File([fileBlob], "result_model.pdb", { type: "text/plain;charset=utf-8" });

	let totLines = [];
	for (var i = 0; i < linesArray.length; i++) {
		let currentLine = linesArray[i];
		if (currentLine.substring(0, 4) == "ATOM") {
			let currNumber = currentLine.substring(23, 26).split(' ').join('') + "-" + currentLine.substring(23, 26).split(' ').join('');
			let currValue = currentLine.substring(62, 66).split(' ').join('');
			lines = [f(currValue).hex(), currNumber];
			totLines.push(lines);
		}
	}

	stage = new NGL.Stage("viewport");

	stage.loadFile(downloadFile).then(function (o) {
		var schemeId = NGL.ColormakerRegistry.addSelectionScheme(totLines, 'pocker miner');
		o.addRepresentation("ribbon", { colorScheme: schemeId });
		o.autoView();
	});

}

function completeForm() {
	$('#btnDownload').show();
	$('#btnClear').show();
	$('#btnSubmit').hide();
	$('#actionSubtitle').html("Download the file:");
	$('.scaleContainer').show();
	$(".preloader").hide();
	$('.beforeComplete').hide();
}

function restartForm() {
	$('chkTermsAndConditions').prop('disabled', false);
	$('#btnDownload').hide();
	$('#btnClear').hide();
	$('#btnSubmit').show();
	$('#actionSubtitle').html("Upload a protein PDB file:");
	$("#files").val(null);
	$("#files").val('');
	$('#btnSelectFiles').html("Choose file");
	$('#chkTermsAndConditions').prop('checked', false);
	$('#viewport').html('');
	$('.scaleLabel').hide();
	$('.scaleContainer').hide();
	$('.beforeComplete').show();

}