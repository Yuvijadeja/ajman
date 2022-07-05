function generatePDF(reportName) {
    var doc = new jsPDF('l', 'pt', 'letter');
    var pageHeight = 0;
    pageHeight = doc.internal.pageSize.height;
    specialElementHandlers = {
        // element with id of "bypass" - jQuery style selector  
        '#bypassme': function (element, renderer) {
            // true = "handled elsewhere, bypass text extraction"
            return true
        }
    };
    margins = {
        top: 150,
        bottom: 60,
        left: 40,
        right: 40,
        width: 600
    };
    var y = 20;
    doc.setLineWidth(2);
    doc.setFontSize(14);
    doc.setTextColor(60, 9, 108);
    doc.text("Online Data Acquisition System - "+reportName, doc.internal.pageSize.width / 2, y = y + 20, {align: 'center'});
    doc.setFontSize(12);
    var date = new Date();
    doc.text("Report generated on: "+ date, doc.internal.pageSize.width / 2, y = y + 20, {align: 'center'});
    
    var tbl = $('#table').clone();
    tbl.find('#bypassme').remove();
    var res = doc.autoTableHtmlToJson(tbl.get(0));

    doc.autoTable(res.columns, res.data, {
        startY: y + 20,
        theme: 'grid',
        showHead: 'everyPage',
        headStyles: {
            lineWidth: 1,
            fillColor: [60, 9, 108],
        },
        styles: {
            minCellHeight: 10,
        }
    })

    const pageCount = doc.internal.getNumberOfPages()

    doc.setFont('helvetica', 'italic')
    doc.setFontSize(9)
    for (var i = 1; i <= pageCount; i++) {
        doc.setPage(i)
        doc.text("Report generated by Technicrafts Enviro Solutions", doc.internal.pageSize.width / 2, doc.internal.pageSize.height - 20,
        {align: 'center'})
    }
    doc.save(reportName+'.pdf');
}