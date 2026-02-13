


$(document).ready(function () {
    $('#result-card').hide();
});

function search() {
    var selectedOption = document.getElementById("selectBox").value;
    var searchContent = document.getElementById("searchInput").value;
    $.get("http://http://8.218.164.134:8000/searchPDB?" + selectedOption + "=" + searchContent, {}, function (data) {
        console.log(data);
        var responseData = JSON.parse(data);

        // <!-- ------------  ------------  ----------- 华丽的分割线 ------------  ------------  ------------ -->
        //更改前：
        // document.getElementById("PDBID").innerText = responseData[0].fields.PDBID;
        // document.getElementById("UniPortID").innerText = responseData[0].fields.UniPortID;
        // document.getElementById("Sequence").innerText = responseData[0].fields.Sequence;
        // document.getElementById("Description").innerText = responseData[0].fields.Description;
        // document.getElementById('structure_image').src = 'http://8.218.164.134:8000/searchPDB_searchimg';
        // document.getElementById("download_link").href = responseData[0].fields.download_link;
        // <!-- ------------  ------------  ----------- 华丽的分割线 ------------  ------------  ------------ -->
        
        // 更改后：
        document.getElementById("UniProtentry").innerText = responseData[0].fields.UniProtentry;
        document.getElementById("PDBDOI").src = responseData[0].fields.PDBDOI;
        document.getElementById("PubMed").innerText = responseData[0].fields.PubMed;
        document.getElementById("Classification").innerText = responseData[0].fields.Classification;
        document.getElementById("Organism").innerText = responseData[0].fields.Organism;
        document.getElementById("Mutation").innerText = responseData[0].fields.Mutation;
        document.getElementById("Gene").innerText = responseData[0].fields.Gene;
        document.getElementById("ExpressionSystem").innerText = responseData[0].fields.ExpressionSystem;
        document.getElementById("Aminoacids").innerText = responseData[0].fields.Aminoacids;
        document.getElementById("Length").innerText = responseData[0].fields.Length;
        document.getElementById("download_link").src = responseData[0].fields.download_link;
        document.getElementById("GOlink").src = responseData[0].fields.GOlink;
        document.getElementById("CellularComponent").innerText = responseData[0].fields.CellularComponent;
        document.getElementById("MolecularFunction").innerText = responseData[0].fields.MolecularFunction;
        document.getElementById("BiologicalProcess").innerText = responseData[0].fields.BiologicalProcess;
        document.getElementById("Submittednames").innerText = responseData[0].fields.Submittednames;
        document.getElementById("Identifier").innerText = responseData[0].fields.Identifier;
        document.getElementById("Component").innerText = responseData[0].fields.Component;
        document.getElementById("Cellularcomponent").innerText = responseData[0].fields.Cellularcomponent;
        document.getElementById("Name").innerText = responseData[0].fields.Name;
        document.getElementById("Orderedlocus").innerText = responseData[0].fields.Orderedlocus;
        document.getElementById("Taxonomicidentifier").innerText = responseData[0].fields.Taxonomicidentifier;
        document.getElementById("Organism").innerText = responseData[0].fields.Organism;
        document.getElementById("Strain").innerText = responseData[0].fields.Strain;
        document.getElementById("Taxonomiclineage").innerText = responseData[0].fields.Taxonomiclineage;
        document.getElementById("Primaryaccession").innerText = responseData[0].fields.Primaryaccession;
        document.getElementById("alpha").innerText = responseData[0].fields.alpha;
        document.getElementById("beta").innerText = responseData[0].fields.beta;
        document.getElementById("coil").innerText = responseData[0].fields.coil;
        document.getElementById("ECODdomainID").innerText = responseData[0].fields.ECODdomainID;
        document.getElementById("ECODarchitecture").innerText = responseData[0].fields.ECODarchitecture;
        document.getElementById("ECODID").innerText = responseData[0].fields.ECODID;
        document.getElementById("ECODPDBdelineation").innerText = responseData[0].fields.ECODPDBdelineation;
        document.getElementById("ECODrenumdelineation").innerText = responseData[0].fields.ECODrenumdelineation;
        document.getElementById("ECODX").innerText = responseData[0].fields.ECODX;
        document.getElementById("ECODH").innerText = responseData[0].fields.ECODH;
        document.getElementById("ECODT").innerText = responseData[0].fields.ECODT;
        document.getElementById("ECODF").innerText = responseData[0].fields.ECODF;
        document.getElementById("CATHID").innerText = responseData[0].fields.CATHID;
        document.getElementById("CATHPDBdelineation").innerText = responseData[0].fields.CATHPDBdelineation;
        document.getElementById("CATHrenumdelineation").innerText = responseData[0].fields.CATHrenumdelineation;
        document.getElementById("CATHclass").innerText = responseData[0].fields.CATHclass;
        document.getElementById("CATHarchitecture").innerText = responseData[0].fields.CATHarchitecture;
        document.getElementById("CATHtopology").innerText = responseData[0].fields.CATHtopology;
        document.getElementById("CATHsupfamily").innerText = responseData[0].fields.CATHsupfamily;
        document.getElementById("SCOPPDBdelineation").innerText = responseData[0].fields.SCOPPDBdelineation;
        document.getElementById("SCOPrenumdelineation").innerText = responseData[0].fields.SCOPrenumdelineation;
        document.getElementById("SCOPclass").innerText = responseData[0].fields.SCOPclass;
        document.getElementById("SCOPfold").innerText = responseData[0].fields.SCOPfold;
        document.getElementById("SCOPsupfamily").innerText = responseData[0].fields.SCOPsupfamily;
        document.getElementById("SCOPfamily").innerText = responseData[0].fields.SCOPfamily;
        document.getElementById("SWORDID").innerText = responseData[0].fields.SWORDID;
        document.getElementById("SWORDquality").innerText = responseData[0].fields.SWORDquality;
        document.getElementById("SWORDrenumdelineation").innerText = responseData[0].fields.SWORDrenumdelineation;
        document.getElementById("SWORDPDBdelineation").innerText = responseData[0].fields.SWORDPDBdelineation;
        document.getElementById("divSE").innerText = responseData[0].fields.divSE;
        document.getElementById("divMM").innerText = responseData[0].fields.divMM;
        document.getElementById("avgRMSF").innerText = responseData[0].fields.avgRMSF;
        document.getElementById("avggyration").innerText = responseData[0].fields.avggyration;
        document.getElementById("contactchain").innerText = responseData[0].fields.contactchain;
        document.getElementById("contactligand").innerText = responseData[0].fields.contactligand;
        document.getElementById("contaction").innerText = responseData[0].fields.contaction;
        document.getElementById("contactnucleotide").innerText = responseData[0].fields.contactnucleotide;
        document.getElementById("nocontact").innerText = responseData[0].fields.nocontact;
        document.getElementById("nonredundantprotein").innerText = responseData[0].fields.nonredundantprotein;
        document.getElementById("nonredundantdomain").innerText = responseData[0].fields.nonredundantdomain;
        document.getElementById("Sequence").innerText = responseData[0].fields.Sequence;
        document.getElementById("Belongstofamilylink").src = responseData[0].fields.Belongstofamilylink;
        document.getElementById("HOGENOM").innerText = responseData[0].fields.HOGENOM;

        // <!-- ------------  ------------  ----------- 华丽的分割线 ------------  ------------  ------------ -->

        // alert("请求成功!");

        // const searchButton = document.getElementById('searchButton');
        // const searchBox = document.querySelector('.search-box');
        // searchButton.addEventListener('click', function () {
        //     overlay.classList.add("hidden");
        //     setTimeout(() => {
        //         overlay.remove();
        //     }, 4000); // Delay the removal after transition ends

        //     searchBox.classList.add('clicked');
        //     $('#result-card').show();
        // });

        const searchcontainer = document.getElementById('container');
        const searchButton = document.getElementById('searchButton');
        const searchBox = document.querySelector('.search-box');
        
        searchButton.addEventListener('click', function () {
            overlay.classList.add("hidden");
            setTimeout(() => {
                overlay.remove();
            }, 4000);
            
            $('#container').hide();
            $('#result-card').show();
        });




    }).fail(function (xhr, textStatus, errorThrown) {
        alert("请求失败:" + errorThrown);


        // const searchButton = document.getElementById('searchButton');
        // const searchBox = document.querySelector('.search-box');
        // searchButton.addEventListener('click', function () {
        //     searchBox.classList.add('clicked');
        //     $('#result-card').show();
        // });
        const searchcontainer = document.getElementById('container');
        const searchButton = document.getElementById('searchButton');
        const searchBox = document.querySelector('.search-box');
        

        
        searchButton.addEventListener('click', function () {
            overlay.classList.add("hidden");
            setTimeout(() => {
                overlay.remove();
            }, 4000);

            $('#container').hide();
            $('#result-card').show();
        });

    });
}

$(document).ready(function () {
    $('#result-card').hide();
});

// $('#searchButton').click(function() {
//     search();
// });

function handleFormSubmit(event) {
    event.preventDefault();

    var searchInput = document.getElementById("searchInput").value.trim();
    if (!searchInput) {
        alert("Please enter search content!");
    } else {
        search();
    }
}

function displayAlert(message) {
    var alertDiv = document.createElement("div");
    alertDiv.classList.add("alert");

    var alertMessage = document.createElement("div");
    alertMessage.classList.add("alert-message");
    alertMessage.innerText = message;

    alertDiv.appendChild(alertMessage);
    document.body.appendChild(alertDiv);

    setTimeout(function () {
        alertDiv.style.display = "none";
    }, 1500);
}