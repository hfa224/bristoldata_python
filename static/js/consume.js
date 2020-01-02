$(document).ready(function() {
    $.ajax({
        url: "https://opendata.bristol.gov.uk/api/records/1.0/search/?dataset=taxi-ranks"
    }).then(function(data) {
        $('.data-nhits').append(data.nhits);
    });
});