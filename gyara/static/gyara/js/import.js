var categories = getCategories();


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getPrediction(name, categoryNode) {
    var csrftoken = getCookie('csrftoken');
    return $.ajax({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        type: "GET",
        url: "/gyara/prediction?description=" + name,
        success: function (responsedata) {
            if (responsedata && responsedata.prediction) {
                $(categoryNode).dropdown('set selected', responsedata.prediction)
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function saveTransaction(dateString, flow, description, value, category) {
    var csrftoken = getCookie('csrftoken');
    var date = dateString.substr(0,4) + "-" + dateString.substr(4,2) + "-" + dateString.substr(6,2);
    value = value.replace(",", ".");
    console.log(date)
    return $.ajax({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        type: "POST",
        url: "/gyara/transactions/add/" + name,
        data: {date: date, flow: flow, description: description, category: category, value: value},
        success: function (responseData) {

        }
    });
}


function getCategories() {
    var csrftoken = getCookie('csrftoken');
    return $.ajax({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        type: "GET",
        url: "/gyara/transactions/cat-view",
        data: {}


    });
}

function addTableRow(row, index) {
    var lastChild = $('#importTable').find('> tbody:last-child');
    var item = "<tr>";
    item = item + "<td>" + row["Datum"] + "</td>";
    item = item + "<td>" + row["Naam / Omschrijving"] + "</td>";
    var IO = row['Af Bij'] === 'Af' ? 'OUT' : 'IN';
    item = item + "<td>" + IO + "</td>";
    item = item + "<td>" + row["Bedrag (EUR)"] + "</td>";
    var categoryDropdown = "<div id=\"category" + index + "\" class=\"ui selection dropdown\">\n" +
        "  <div class=\"text\"></div>\n" +
        "  <i class=\"dropdown icon\"></i>\n" +
        "</div>";


    item = item + "<td>" + categoryDropdown + "</td>";
    item = item + "<td>" + "<a id=\"predict" + index + "\" class=\"ui button predict\">Predict</a>" +
        "<a id=\"save" + index + "\" class=\"ui positive button\">Save</a>" +
        "<a id=\"discard" + index + "\" class=\"ui button\">Discard</a>" + "</td>";


    lastChild.append(item);

    $("#predict" + index).click(function () {
        var name = $(this).closest('tr').find('td:nth-child(2)').text();
        var categoryDropdown = $(this).closest('tr').find('td:nth-child(5) div.ui.selection.dropdown');
        getPrediction(name, categoryDropdown);
    });

    $("#discard" + index).click(function () {
        $(this).closest('tr').remove();
    });

    $("#save" + index).click(function () {
        var tableRow = $(this).closest('tr');
        var dateString = tableRow.find('td:nth-child(1)').text();
        var description = tableRow.find('td:nth-child(2)').text();
        var flow = tableRow.find('td:nth-child(3)').text();
        var value = tableRow.find('td:nth-child(4)').text();
        var category = tableRow.find('td:nth-child(5)').dropdown('get value');
        saveTransaction(dateString, flow, description, value, category).done(function() {
           tableRow.remove();
        });
    });

    return categories.done(function (data) {
        var dataJSON = JSON.parse(data);
        var dataCat = [];
        for (var k = 0; k < dataJSON.length; k++) {
            dataCat.push({
                name: dataJSON[k].fields.name,
                value: dataJSON[k].pk
            })
        }
        return $('#category' + index).dropdown({values: dataCat});
    })


}

function upload(evt) {
    if (!browserSupportFileUpload()) {
        alert('The File APIs are not fully supported in this browser!');
    } else {
        var data = null;
        var file = evt.target.files[0];
        var reader = new FileReader();
        reader.readAsText(file);
        reader.onload = function (event) {
            var csvData = event.target.result;
            data = jQuery.csv.toObjects(csvData);
            if (data && data.length > 0) {
                for (i = 0; i < data.length; i++) {
                    // {#                            csvRowToForm(data[i]);#}
                    addTableRow(data[i], i);
                }
                // {#                        deleteLast(".cloneable:last", "form")#}
            } else {
                alert('No data to import!');
            }
        };
        reader.onerror = function () {
            alert('Unable to read ' + file.fileName);
        };
    }
}

function browserSupportFileUpload() {
    var isCompatible = false;
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        isCompatible = true;
    }
    return isCompatible;
}

$(document).ready(function () {

    document.getElementById('txtFileUpload').addEventListener('change', upload, false);
    // Method that checks that the browser supports the HTML5 File API
    $(".delete-row").click(function () {
        $(this).parent().hide('slow', function () {
            $(this).remove()
        });

    });


});

