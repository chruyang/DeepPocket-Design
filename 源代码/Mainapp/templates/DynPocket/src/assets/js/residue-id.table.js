function settable(){
    var pastA = "AAA";
    var currentA;

    var idarr = ["", "", "","",""]; 
    var valuearr = ["", "", "","",""]; 

    for (var i = 0,num = -1; num < 5; i++) {
        let currentLine = linesArray[i];
        if (currentLine.substring(0, 4) == "ATOM") {
            currentA = currentLine.substring(17, 20).split(' ').join('');
            if (currentA != pastA) {
                num++;
                let currValue = currentLine.substring(62, 66).split(' ').join('');
                idarr[num] = currentA;
                valuearr[num] = currValue;
            }
            pastA = currentA;
        }
    }

    // for (var i = 0; i < idarr.length; i++) {
    //     document.getElementById("row1col" + (i + 1)).innerText = idarr[i];
    // }
    // for (var j = 0; j < valuearr.length; j++) {
    //     document.getElementById("row2col" + (j + 1)).innerText = valuearr[j];
    // }

    document.getElementById("row1col1").innerText = idarr[0];
    document.getElementById("row1col2").innerText = idarr[1];
    document.getElementById("row1col3").innerText = idarr[2];
    document.getElementById("row1col4").innerText = idarr[3];
    document.getElementById("row1col5").innerText = idarr[4];
    document.getElementById("row2col1").innerText = valuearr[0];
    document.getElementById("row2col2").innerText = valuearr[1];
    document.getElementById("row2col3").innerText = valuearr[2];
    document.getElementById("row2col4").innerText = valuearr[3];
    document.getElementById("row2col5").innerText = valuearr[4];
}