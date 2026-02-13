document.addEventListener('DOMContentLoaded', function () {// 页面加载完成后执行
    fetch('data.json') //GET 获取'data.json'
        .then(response => response.json()) 
        .then(data => {
            var processedData = processData(data); 
            renderChart(processedData); 
        })
        .catch(error => console.error('获取数据失败:', error)); 
});

function processData(data) {
    var processedData = [
        { value: 0, name: '0.00~0.25' }, 
        { value: 0, name: '0.25~0.50' }, 
        { value: 0, name: '0.50~0.75' },
        { value: 0, name: '0.75~1.00' }   
    ];
    for (var key in data) {
        var probability = parseFloat(data[key]); 
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
    return processedData;
}

function renderChart(data) {
    // 找到图表容器
    var chartContainer = document.getElementsByClassName("chart")[0];

    // 使用 ECharts 初始化图表
    var chart = echarts.init(chartContainer);

    // 配置项
    var option = {
        title: {
            text: 'Probability distribution of residues forming pockets', 
            left: 'center', 
            textStyle: {
                fontSize: 13, 
                color: '#333', 
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






// ---------------------------------------- 注意！！！！！ ---------------------------------------- 

/* JSON 数据文件名为 data.json，内容结构如下：

json{
    "GLY-A-1": 0.06,
    "ASN-A-2": 0.12,
    "ASN-A-3": 0.17,
    "VAL-A-4": 0.17,
    "VAL-A-5": 0.24,
    "VAL-A-6": 0.39,
    "LEU-A-7": 0.84,
    "GLY-A-8": 0.66,
    "THR-A-9": 0.60,
    "GLN-A-10": 0.75,
    "TRP-A-11": 0.96,
    "GLY-A-12": 0.91,
    "ASP-A-13": 0.94,
    "GLU-A-14": 0.87,
    "GLY-A-15": 0.92,
    "LYS-A-16": 0.89,
    "GLY-A-17": 0.89,
    "LYS-A-18": 0.93,
    "ILE-A-19": 0.84,
    "VAL-A-20": 0.74
}

*/

// ---------------------------------------- 注意！！！！！ ---------------------------------------- 
