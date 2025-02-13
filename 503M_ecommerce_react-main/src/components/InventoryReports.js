// src/components/InventoryReports.js
import React from 'react';
import { Box, Button} from '@mui/material';
import { jsPDF } from 'jspdf';
import Chart from 'chart.js/auto';

const InventoryReports = ({ turnoverData, popularProductsData, demandPredictionData }) => {

  const generatePDF = async () => {
    const pdf = new jsPDF('p', 'mm', 'a4');
    let pageHeight = pdf.internal.pageSize.height;
  const getCurrentDate = () => {
    const today = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return today.toLocaleDateString(undefined, options);
    };
    

    //page number
    const addPageNumber = (pageNum) => {
      pdf.setFontSize(10);
      pdf.setTextColor('#999');
      pdf.text(`Page ${pageNum}`, pdf.internal.pageSize.width - 20, pageHeight - 10);
    };

    //cover Page
    pdf.setFontSize(26);
    pdf.setTextColor('#4A90E2');
    pdf.text("Inventory Management Report", 105, 50, null, null, 'center');
    
    pdf.setFontSize(14);
    pdf.setTextColor('#333');
    pdf.text("Prepared for: Gaming Console Store", 105, 65, null, null, 'center');
    
    pdf.setFontSize(12);
    pdf.setTextColor('#666');
    pdf.text(`Date: ${getCurrentDate()}`, 105, 75, null, null, 'center');
    
    pdf.setFontSize(16);
    pdf.setTextColor('#333');
    pdf.text("Report Overview", 105, 100, null, null, 'center');
    
    pdf.setFontSize(12);
    pdf.setTextColor('#666');
    pdf.text("This comprehensive report provides insights into the company's inventory management process, including turnover rates, popular products, and demand forecasts. These metrics help the company make informed decisions to optimize stock levels and meet customer demands effectively.",
      20, 120, { maxWidth: 170, align: 'left' }
    );

    pdf.setTextColor('#333');
    pdf.text(
      "In this report, you will find:",
      20, 150
    );

    pdf.setTextColor('#333');
    pdf.text(
      "• Monthly inventory turnover rates for understanding stock cycles.\n" +
      "• Analysis of the most popular products based on recent data.\n" +
      "• Quarterly demand predictions to plan future inventory needs.\n",
      20, 160
    );

    pdf.setFontSize(14);
    pdf.setTextColor('#4A90E2');
    pdf.text("", 105, 190, null, null, 'center');
    addPageNumber(1);
    pdf.addPage();

    //function to create chart image with enhanced styling and vibrant colors
    const createChartImage = async (data, type = 'bar', title = '', bgColor) => {
      return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 400;
        const ctx = canvas.getContext('2d');

        const chart = new Chart(ctx, {
          type,
          data: {
            labels: data.labels,
            datasets: [{
              label: title,
              data: data.values,
              backgroundColor: bgColor,
              borderColor: '#333',
              borderWidth: 2,
            }]
          },
          options: {
            responsive: false,
            plugins: {
              legend: { display: true, position: 'top', labels: { color: '#333', font: { size: 14 } } },
              title: { display: true, text: title, color: '#333', font: { size: 18, weight: 'bold' } },
            },
            scales: {
              x: {
                grid: { color: 'rgba(200, 200, 200, 0.3)' },
                ticks: { color: '#333', font: { size: 12 } }
              },
              y: {
                grid: { color: 'rgba(200, 200, 200, 0.3)' },
                ticks: { color: '#333', font: { size: 12 } }
              }
            }
          }
        });

        setTimeout(() => {
          const imgData = chart.toBase64Image();
          chart.destroy();
          resolve(imgData);
        }, 100);
      });
    };

    try {
      const turnoverChartImage = await createChartImage(
        turnoverData,
        'bar',
        'Monthly Inventory Turnover',
        ['#FF6B6B', '#FAD02E', '#6BCB77', '#4A90E2']
      );

      const popularProductsChartImage = await createChartImage(
        popularProductsData,
        'bar',
        'Most Popular Products',
        ['#FF6384', '#36A2EB', '#FFCE56', '#FF9F40']
      );

      const demandPredictionChartImage = await createChartImage(
        demandPredictionData,
        'line',
        'Quarterly Demand Prediction',
        ['#36A2EB']
      );

      pdf.setTextColor('#4A90E2');
      pdf.setFontSize(18);
      pdf.text("Monthly Inventory Turnover", 10, 20);
      pdf.setFontSize(12);
      pdf.setTextColor('#666');
      pdf.text(
        "This chart provides a monthly view of inventory turnover, helping to gauge how frequently stock is cycled. High turnover rates suggest faster sales or efficient stock management, while lower rates may indicate overstock or slow-moving inventory.",
        10, 30, { maxWidth: 180 }
      );
      pdf.addImage(turnoverChartImage, 'PNG', 10, 60, 180, 90);
      addPageNumber(2);
      pdf.addPage();

      pdf.setTextColor('#4A90E2');
      pdf.setFontSize(18);
      pdf.text("Most Popular Products", 10, 20);
      pdf.setFontSize(12);
      pdf.setTextColor('#666');
      pdf.text(
        "The most popular products are shown here, highlighting the top-selling items based on recent sales data. These products drive the highest customer interest, making them crucial for restocking and promotional efforts.",
        10, 30, { maxWidth: 180 }
      );
      pdf.addImage(popularProductsChartImage, 'PNG', 10, 60, 180, 90);
      addPageNumber(3);
      pdf.addPage();

      pdf.setTextColor('#4A90E2');
      pdf.setFontSize(18);
      pdf.text("Quarterly Demand Prediction", 10, 20);
      pdf.setFontSize(12);
      pdf.setTextColor('#666');
      pdf.text(
        "Based on historical trends and current sales data, this chart forecasts demand for the upcoming quarters. Accurate demand predictions help in planning stock levels, ensuring timely availability of high-demand products.",
        10, 30, { maxWidth: 180 }
      );
      pdf.addImage(demandPredictionChartImage, 'PNG', 10, 60, 180, 90);
      addPageNumber(4);

      pdf.save('Inventory_Report.pdf');
    } catch (error) {
      console.error("Error generating PDF:", error);
    }
  };
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
      <Button variant="contained" color="primary" onClick={generatePDF} sx={{ boxShadow: 3 }}>
        Generate PDF Report
      </Button>
    </Box>
  );
};

export default InventoryReports;
