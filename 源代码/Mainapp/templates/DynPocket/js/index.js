
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
          { value: 1048, name: '0.00~0.25' },
          { value: 735, name: '0.25~0.50' },
          { value: 580, name: '0.50~0.75' },
          { value: 484, name: '0.75~1.00' },
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
  
// 将配置应用到图表中
chart.setOption(option);


function goToPage(page) {
  if(page == 'Home') {
    /* 居中警告框 */
      window.location.href = 'Home.html';
  } else if (page === 'search') {
      window.location.href = 'search.html';
  } else if (page === 'prediction_input') {
      window.location.href = 'prediction_input.html';
  } else if (page == 'Help') {
    window.location.href = 'Help.html';
  } else if (page == 'User') {
    window.location.href = 'User.html';
  }
}