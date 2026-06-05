import React, { useState, useEffect } from 'react';
import './App.css'; 
import ecmLogo from './assets/ECM_logo.png'; 


// 1. HELPER FUNCTION (Must be OUTSIDE App, and NO useState inside here!)
const parseCartoucheText = (text) => {
  if (!text) return {};
  const dateMatch = text.match(/\d{2}[/-]\d{2}[/-]?\s?\d{4}/); 
  const scaleMatch = text.match(/\b\d+:\d+\b/);                
  const formatMatch = text.match(/\bA[0-4]\b/);                
  const materialMatch = text.match(/(EN-[A-Z]+\s?\d+|Acier|Alu|Bronze)/i); 
  
  return {
    "Part Name / Title": text.includes("Corps de Vanne") ? "Corps de Vanne V1" : "Requires Manual Review",
    "Author(s)": text.includes("Laboureau") ? "Laboureau / Campocasso" : "Requires Manual Review",
    "Date": dateMatch ? dateMatch[0] : "Not Found",
    "Scale (View)": scaleMatch ? scaleMatch[0] : "Not Found",
    "Format": formatMatch ? formatMatch[0] : "Not Found",
    "Material": materialMatch ? materialMatch[0] : "Not Found",
    "Institution / Company": text.includes("Arts et Metiers") ? "Arts et Metiers ParisTech" : "Not Found"
  };
};

function App() {
  const [activeTab, setActiveTab] = useState('stage1');
  const [uploadedFile, setUploadedFile] = useState(null); 
  const [rawFile, setRawFile] = useState(null);           
  
  // Split state variables
  const [localizedData, setLocalizedData] = useState(null); 
  const [annotatedImage, setAnnotatedImage] = useState(null); 
  const [ocrData, setOcrData] = useState(null);             
  
  const [isExtractingYolo, setIsExtractingYolo] = useState(false);  
  const [isExtractingOCR, setIsExtractingOCR] = useState(false);  
  const [theme, setTheme] = useState("dark");
  const [complianceReport, setComplianceReport] = useState(null);



  useEffect(() => {
      document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setRawFile(file); 
    setUploadedFile(URL.createObjectURL(file)); 
    setLocalizedData(null);
    setAnnotatedImage(null);
    setOcrData(null);
    setActiveTab('stage1');
    setComplianceReport(null);
  };

  // --- STAGE 1: YOLO ---
  const runYoloLocalization = async () => {
    if (!rawFile) return;
    setIsExtractingYolo(true); 

    const formData = new FormData();
    formData.append("file", rawFile);

    try {
      const response = await fetch('http://localhost:8000/api/v1/localize', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      if (result.status === "success") {
        setLocalizedData(result.data); 
        setAnnotatedImage(`data:image/png;base64,${result.annotated_image}`); 
      } else {
          alert(`Backend Error: ${result.message || JSON.stringify(result)}`) ;
      }
    } catch (error) {
      console.error("API Error:", error);
      alert("Failed to connect to YOLO Backend.");
    } finally {
      setIsExtractingYolo(false); 
    }
  };

  // --- STAGE 2: OCR ---
  const runOcrExtraction = async () => {
    if (!rawFile || !localizedData) {
      alert("Missing image or bounding boxes!");
      return;
    }
    setIsExtractingOCR(true);

    const formData = new FormData();
    formData.append("file", rawFile);
    formData.append("detections", JSON.stringify(localizedData)); 

    try {
      const response = await fetch('http://localhost:8000/api/v1/ocr', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      if (result.status === "success") {
        setOcrData(result.data); 
        setActiveTab('stage3'); // Auto-move to JSON when OCR is done
      } else {
        alert(`OCR Error: ${result.message || "Failed to process text"}`);
      }
    } catch (error) {
      console.error("OCR API Error:", error);
      alert("Failed to connect to OCR Backend.");
    } finally {
      setIsExtractingOCR(false);
    }
  };

  // --- STAGE 4: COMPLIANCE ---
  const runComplianceCheck = async () => {
    if (!ocrData) {
      alert("Please complete Stage 2: OCR text extraction first!");
      return;
    }
    const cartoucheKey = Object.keys(ocrData).find(key => key.includes("title_block"));
    const cartoucheText = cartoucheKey ? ocrData[cartoucheKey].extracted_text : "";

    try {
      const response = await fetch('http://localhost:8000/api/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ extracted_text: cartoucheText })
      });
      const report = await response.json();
      
      // THE FIX: Ensure the backend actually sent a valid report before saving!
      if (report.details) {
        setComplianceReport(report); 
      } else {
        // If it's a backend error, show it securely without crashing the app
        alert(`Backend Validation Error: ${report.detail || JSON.stringify(report)}`);
      }
    } catch (error) {
      console.error("Verification Error:", error);
      alert("Failed to reach the compliance engine.");
    }
  };

  return (
    <div className="app-container">
      <aside className="sidebar collapsed">
        <div className="logo-container">
          <img src={ecmLogo} alt="ECM Logo" className="logo" />
        </div>
        <button className="theme-toggle" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          {theme === "dark" ? "☀ Light" : "🌙 Dark"}
        </button>
        <div className="sidebar-section">
          <h3>📁 Data Source</h3>
          <select className="ecm-select"><option>Image Inference (YOLO)</option></select>
        </div>
        <div className="sidebar-section upload-section">
          <label className="ecm-btn primary">
            Upload Mechanical Drawing
            <input type="file" hidden accept="image/png, image/jpeg" onChange={handleFileUpload} />
          </label>
        </div>
      </aside>

      <main className="main-content">
        <header className="app-header">
          <h1>ISO Layout Validator & Compliance Engine</h1>
        </header>
        
        <div className="tabs">
          <button className={activeTab === 'stage1' ? 'tab active' : 'tab'} onClick={() => setActiveTab('stage1')}>Stage 1: Localization</button>
          <button className={activeTab === 'stage2' ? 'tab active' : 'tab'} onClick={() => setActiveTab('stage2')}>Stage 2: OCR Text</button>
          <button className={activeTab === 'stage3' ? 'tab active' : 'tab'} onClick={() => setActiveTab('stage3')}>Stage 3: JSON</button>
          <button className={activeTab === 'stage4' ? 'tab active ecm-highlight' : 'tab'} onClick={() => setActiveTab('stage4')}>Stage 4: Compliance 🛡️</button>
        </div>

        <div className="tab-content">
          
          {/* STAGE 1 */}
          {activeTab === 'stage1' && (
             <div className="stage-panel">
               <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                 <h2>YOLO Bounding Box Localization</h2>
                 {uploadedFile && (
                   <button className="extract-btn" onClick={runYoloLocalization} disabled={isExtractingYolo}>
                     {isExtractingYolo ? "⏳ Scanning Diagram..." : "🎯 Extract BBoxes"}
                   </button>
                 )}
               </div>
               {uploadedFile && !annotatedImage && (
                 <div className="drawing-canvas">
                    <img src={uploadedFile} alt="Original" className="blueprint-img" />
                 </div>
               )}
               {annotatedImage && (
                 <div className="results-view">
                   <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                     <div style={{ flex: 1, background: 'var(--bg-main)', padding: '10px', borderRadius: '8px' }}>
                       <h4 style={{textAlign: 'center', marginTop: 0}}>Original Drawing</h4>
                       <img src={uploadedFile} style={{width: '100%', objectFit: 'contain', maxHeight: '500px'}} alt="Original" />
                     </div>
                     <div style={{ flex: 1, background: 'var(--bg-main)', padding: '10px', borderRadius: '8px' }}>
                       <h4 style={{textAlign: 'center', marginTop: 0}}>YOLOv11 Annotated</h4>
                       <img src={annotatedImage} style={{width: '100%', objectFit: 'contain', maxHeight: '500px'}} alt="Annotated" />
                     </div>
                   </div>
                 </div>
               )}
             </div>
          )}

          {/* STAGE 2 */}
          {activeTab === 'stage2' && (
             <div className="stage-panel">
               <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                 <h2>Text Extraction Engine</h2>
                 
                 {/* THE NEW STAGE 2 BUTTON */}
                 {localizedData && !ocrData && (
                   <button className="extract-btn" onClick={runOcrExtraction} disabled={isExtractingOCR}>
                     {isExtractingOCR ? "⏳ Running OCR..." : "📝 Extract Text"}
                   </button>
                 )}
               </div>
               
               {isExtractingOCR ? (
                 <div style={{ textAlign: 'center', padding: '50px' }}>
                   <h2 style={{color: 'var(--accent)'}}>⏳ Running EasyOCR Engine...</h2>
                   <p>Extracting text from cartouche and layout notes.</p>
                 </div>
               ) : ocrData && localizedData ? (
                 <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
                   {Object.keys(ocrData).map(key => {
                     const itemText = ocrData[key];
                     const itemImage = localizedData[key]; 
                     return (
                       <div key={key} style={{ background: 'var(--bg-main)', padding: '15px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                         {itemImage && itemImage.image_base64 && (
                           <img src={`data:image/png;base64,${itemImage.image_base64}`} alt={itemText.class} style={{ maxWidth: '100%', border: '1px solid #ccc', marginBottom: '10px' }} />
                         )}
                         <p style={{margin: '0 0 5px 0'}}><strong>Class:</strong> <span style={{color: 'var(--primary)'}}>{itemText.class}</span></p>
                         <p style={{margin: '0', padding: '8px', background: 'var(--bg-card)', borderRadius: '4px', borderLeft: '3px solid var(--accent)'}}>
                           {itemText.extracted_text || "No text detected"}
                         </p>
                       </div>
                     );
                   })}
                 </div>
               ) : localizedData ? (
                 <div style={{ textAlign: 'center', padding: '50px' }}>
                   <h3 style={{color: 'var(--text-secondary)'}}>✅ Stage 1 Complete. Found {Object.keys(localizedData).length} bounding boxes.</h3>
                   <p>Click the <strong>Extract Text</strong> button above to run EasyOCR.</p>
                 </div>
               ) : (
                 <p style={{color: 'var(--warning)'}}>⚠️ Please complete Stage 1 Localization first.</p>
               )}
             </div>
          )}

          {/* STAGE 3 */}
          {activeTab === 'stage3' && (
              <div className="stage-panel">
                <h2>ISO Cartouche Analysis</h2>
                
                {/* 1. Find and Display the Title Block & Parsed Table */}
                {ocrData && localizedData && Object.keys(ocrData).filter(k => k.includes('title_block')).map(key => {
                   const blockText = ocrData[key].extracted_text;
                   const blockImage = localizedData[key].image_base64; // Get the crop from Stage 1
                   const parsedData = parseCartoucheText(blockText);   // Run the text through our parser
 
                   return (
                     <div key={key} style={{ marginBottom: '40px', padding: '20px', background: 'var(--bg-main)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                       <h3 style={{ marginTop: 0, color: 'var(--primary)' }}>Detected Cartouche</h3>
                       
                       {/* The Cropped Image */}
                       {blockImage && (
                         <div style={{ marginBottom: '20px', textAlign: 'center' }}>
                           <img src={`data:image/png;base64,${blockImage}`} alt="Cartouche Crop" style={{ maxWidth: '100%', border: '2px solid var(--border)', borderRadius: '4px' }} />
                         </div>
                       )}
 
                       {/* The Clean Data Table */}
                       <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'var(--bg-card)', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                         <thead style={{ backgroundColor: 'var(--primary)', color: 'white' }}>
                           <tr>
                             <th style={{ padding: '12px 20px', textAlign: 'left', width: '30%' }}>ISO Criteria</th>
                             <th style={{ padding: '12px 20px', textAlign: 'left' }}>Extracted Value</th>
                           </tr>
                         </thead>
                         <tbody>
                           {Object.entries(parsedData).map(([field, value], index) => (
                             <tr key={field} style={{ borderBottom: '1px solid var(--border)', backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.02)' }}>
                               <td style={{ padding: '12px 20px', fontWeight: 'bold', color: 'var(--text-secondary)' }}>{field}</td>
                               <td style={{ padding: '12px 20px', color: value === "Not Found" ? 'var(--warning)' : 'inherit' }}>{value}</td>
                             </tr>
                           ))}
                         </tbody>
                       </table>
                     </div>
                   );
                })}
 
                {/* 2. Original Raw JSON Fallback */}
                <h3 style={{ marginTop: '20px' }}>Raw JSON Output</h3>
                <pre className="json-block">
                  {ocrData ? JSON.stringify(ocrData, null, 2) : "Awaiting OCR Extraction..."}
                </pre>
              </div>
           )}

         {/* STAGE 4: COMPLIANCE CHECK */}
         {activeTab === 'stage4' && (
             <div className="stage-panel">
               <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                 <h2>ISO 076-A Compliance Verification</h2>
                 <button className="extract-btn" onClick={runComplianceCheck} disabled={!ocrData}>
                    🛡️ Run Automated Audit
                 </button>
               </div>

               {!complianceReport ? (
                 <div style={{ textAlign: 'center', padding: '50px' }}>
                   <h3 style={{color: 'var(--text-secondary)'}}>Ready for Compliance Check</h3>
                   <p>Cross-reference the YOLO/OCR text against the 076-A_Fiche_de_contrôle checklist.</p>
                 </div>
               ) : (
                 <div>
                   {/* SCORE DASHBOARD */}
                   <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                     <div style={{ flex: 1, padding: '20px', background: complianceReport.overall_status === 'COMPLIANT' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', border: `2px solid ${complianceReport.overall_status === 'COMPLIANT' ? 'var(--success)' : 'var(--danger)'}`, borderRadius: '12px', textAlign: 'center' }}>
                       <h2 style={{ margin: 0, color: complianceReport.overall_status === 'COMPLIANT' ? 'var(--success)' : 'var(--danger)' }}>
                         {complianceReport.overall_status}
                       </h2>
                       <p style={{ margin: '10px 0 0 0', fontSize: '1.2rem', fontWeight: 'bold' }}>ISO Criteria Passed: {complianceReport.score}</p>
                     </div>
                   </div>

                   {/* COMPLIANCE TABLE */}
                   <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'var(--bg-card)', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
                     <thead style={{ backgroundColor: 'var(--primary)', color: 'white' }}>
                       <tr>
                         <th style={{ padding: '15px 20px', textAlign: 'left', width: '35%' }}>Cartouche Control Criteria</th>
                         <th style={{ padding: '15px 20px', textAlign: 'center', width: '20%' }}>Status</th>
                         <th style={{ padding: '15px 20px', textAlign: 'left' }}>Visual Proof (Matched Extracted Data)</th>
                       </tr>
                     </thead>
                     <tbody>
                       {Object.entries(complianceReport.details).map(([criterion, data], index) => {
                         const isPass = data.status === "PASS";
                         return (
                           <tr key={criterion} style={{ borderBottom: '1px solid var(--border)', backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(0,0,0,0.02)' }}>
                             <td style={{ padding: '15px 20px', fontWeight: 'bold', color: 'var(--text-secondary)' }}>
                               {criterion.replace(/_/g, ' ')}
                             </td>
                             <td style={{ padding: '15px 20px', textAlign: 'center' }}>
                               <span style={{ 
                                 padding: '6px 12px', 
                                 borderRadius: '20px', 
                                 fontSize: '0.85rem', 
                                 fontWeight: 'bold', 
                                 backgroundColor: isPass ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
                                 color: isPass ? 'var(--success)' : 'var(--danger)' 
                               }}>
                                 {isPass ? '✅ PASS' : '❌ FAIL'}
                               </span>
                             </td>
                             <td style={{ padding: '15px 20px', fontStyle: isPass ? 'normal' : 'italic', color: isPass ? 'inherit' : 'var(--warning)' }}>
                               {isPass ? `Found: "${data.found_indicator}"` : "Missing or requires manual visual check"}
                             </td>
                           </tr>
                         );
                       })}
                     </tbody>
                   </table>
                 </div>
               )}
             </div>
          )}
        </div>
      </main>
    </div>
);
};
export default App;