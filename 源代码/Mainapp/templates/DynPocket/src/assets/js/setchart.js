function setchart() {
    // // 创建一个 FileReader 对象
    var fileReader = new FileReader();
    // 定义 onload 回调函数，以便在文件读取完成时执行
    fileReader.onload = function (event) {
        // 通过 event.target.result 获取文件内容
        var fileContent = event.target.result;
        // 打印文件内容到控制台
        console.log(fileContent);
    };
    // 以文本形式读取 Blob 对象的内容
    fileReader.readAsText(downloadFile);
    // alert("linesArray.length=" + linesArray.length);
    //////////////////////////////////////////////////////
    processData();
    renderChart();
}

var processedData = [
    { value: 0, name: '0.00~0.25' },
    { value: 0, name: '0.25~0.50' },
    { value: 0, name: '0.50~0.75' },
    { value: 0, name: '0.75~1.00' }
];


function processData() {

    var pastA = "AAA";
    var currentA;

    for (var i = 0; i < linesArray.length; i++) {
        let currentLine = linesArray[i];
        if (currentLine.substring(0, 4) == "ATOM") {

            currentA = currentLine.substring(17, 20).split(' ').join('');
            if (currentA != pastA) {

                let currValue = currentLine.substring(62, 66).split(' ').join('');
                let probability = parseFloat(currValue);

                if (probability >= 0 && probability < 0.25) {
                    processedData[0].value++;
                } else if (probability >= 0.25 && probability < 0.50) {
                    processedData[1].value++;
                } else if (probability >= 0.50 && probability < 0.75) {
                    processedData[2].value++;
                } else if (probability >= 0.75 && probability <= 1.00) {
                    processedData[3].value++;
                }

            }
            pastA = currentA;
        }
    }

    // alert("processedData[0].value=" + processedData[0].value);
    // alert("processedData[1].value=" + processedData[1].value);
    // alert("processedData[2].value=" + processedData[2].value);
    // alert("processedData[3].value=" + processedData[3].value);

}


function renderChart() {

    // alert("processedData[0].value=" + processedData[0].value);
    // alert("processedData[1].value=" + processedData[1].value);
    // alert("processedData[2].value=" + processedData[2].value);
    // alert("processedData[3].value=" + processedData[3].value);

    // 找到图表容器
    var chartContainer = document.getElementsByClassName("chart")[0];

    // 使用 ECharts 初始化图表
    var chart = echarts.init(chartContainer);


    var option = {
        title: {
            text: 'Probability distribution of residues forming pockets',
            left: 'center',
            textStyle: {
                fontSize: 13, // 设置字体大小
                color: '#333', // 设置字体颜色
                fontFamily: 'Times New Roman, serif',
                fontWeight: 'normal',
            },
        },
        tooltip: {
            trigger: 'item'
        },
        series: [
            {
                name: 'Statistics',
                type: 'pie',
                radius: '50%',
                data: [
                    { value: processedData[0].value, name: '0.00~0.25' },
                    { value: processedData[1].value, name: '0.25~0.50' },
                    { value: processedData[2].value, name: '0.50~0.75' },
                    { value: processedData[3].value, name: '0.75~1.00' },
                ],
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };

    chart.setOption(option);

}





///////////////////////////////





