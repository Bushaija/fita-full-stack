"use client";

import React, { useMemo, useCallback } from "react";
import {
  ReportTitle,
} from "@/components/financial";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useReportData } from "@/hooks/useReportData";
import { useChangesInNetAssetsCalculations } from "@/hooks/useChangesInNetAssetsCalculations";

// Import our custom components and hooks
import {
  NetAssetsRowGroup,
  NetAssetsSummaryRow,
  DynamicFinancialTable,
  DynamicSectionGroup,
  DynamicSubsectionGroup,
  SeparatorRow,
  ChangesInNetAssetsActions,
  ToastManager,
  LoadingState,
  ErrorState
} from "./components";
import { useChangesInNetAssetsPage } from "./hooks";

export default function ChangesInNetAssetsPage() {
  // Get report data from the hook
  const { title, sections, loading, error } = useReportData('changes-assets');
  
  // Use the custom hook for calculations
  const netAssets = useChangesInNetAssetsCalculations(sections, loading);
  
  // Use our custom page hook
  const {
    isEditMode,
    setIsEditMode,
    editedValues,
    errors,
    isSaving,
    getSummaryValues,
    handleValueChange,
    getValue,
    calculateTotal,
    generateRowId,
    handleSaveChanges,
    handleCancelEdits
  } = useChangesInNetAssetsPage(sections);
  
  // Handle print action
  const handlePrint = useCallback(() => window.print(), []);
  
  // Handle retry action
  const handleRetry = useCallback(() => {
    // Reload the page as a simple way to retry
    window.location.reload();
  }, []);
  
  // Memoize columns definition
  const columns = useMemo(() => [
    { key: 'description', label: 'Description' },
    { key: 'surplus', label: 'Accumulated Surplus/Loss (Frw)' },
    { key: 'adjustments', label: 'Adjustments (Frw)' },
    { key: 'total', label: 'Total (Frw)' },
  ], []);
  
  // Check if there are any changes
  const hasChanges = Object.keys(editedValues).length > 0;
  
  // Check if there are any errors
  const hasErrors = Object.keys(errors).length > 0;
  
  // Get summary values - memoized to avoid recalculation
  const summaryValues = useMemo(() => getSummaryValues(), [getSummaryValues]);
  
  // If loading, show skeleton
  if (loading) {
    return <LoadingState />;
  }
  
  // If error, show error message
  if (error) {
    return <ErrorState message={error} onRetry={handleRetry} />;
  }
  
  return (
    <ToastManager>
      {(showToast) => (
        <TooltipProvider>
          <div className="container mx-auto py-8 print:py-4 max-w-7xl">
            <ChangesInNetAssetsActions
              isEditMode={isEditMode}
              isSaving={isSaving}
              hasErrors={hasErrors}
              hasChanges={hasChanges}
              onEdit={() => setIsEditMode(true)}
              onSave={() => {
                handleSaveChanges().then(() => {
                  showToast({
                    message: "Changes saved successfully!",
                    type: "success"
                  });
                }).catch(() => {
                  showToast({
                    message: "Failed to save changes. Please try again.",
                    type: "error"
                  });
                });
              }}
              onCancel={handleCancelEdits}
              onPrint={handlePrint}
            />
            
            <ReportTitle 
              governmentBody={title.governmentBody}
              program={title.program}
              reportType={title.reportType}
              statement={title.statement}
            />
            
            <div className="mt-4 financial-table print-include">
              <DynamicFinancialTable 
                columns={columns}
                className="print-include" 
                caption="Statement of Changes in Net Assets"
                ariaLabel="Statement of Changes in Net Assets table"
              >
                {/* Dynamically render sections */}
                {sections.map((section) => (
                  <DynamicSectionGroup key={section.key} title={section.title}>
                    {/* Render subsections using flatMap for cleaner rendering */}
                    {section.subsections?.flatMap((subsection) => [
                      <DynamicSubsectionGroup key={subsection.key} title={subsection.title} className="pl-4">
                        <NetAssetsRowGroup
                          rows={subsection.rows}
                          sectionKey={section.key}
                          subsectionKey={subsection.key}
                          isEditMode={isEditMode}
                          errors={errors}
                          onValueChange={handleValueChange}
                          getValue={getValue}
                          calculateTotal={calculateTotal}
                          generateRowId={generateRowId}
                        />
                      </DynamicSubsectionGroup>,
                      <SeparatorRow key={`${subsection.key}-sep`} />
                    ])}
                    
                    {/* Show non-subsectioned rows */}
                    {section.rows.length > 0 && (
                      <>
                        <NetAssetsRowGroup
                          rows={section.rows}
                          sectionKey={section.key}
                          isEditMode={isEditMode}
                          errors={errors}
                          onValueChange={handleValueChange}
                          getValue={getValue}
                          calculateTotal={calculateTotal}
                          generateRowId={generateRowId}
                        />
                        <SeparatorRow />
                      </>
                    )}
                    
                    {section.isSummarySection && (
                      <NetAssetsSummaryRow 
                        label="TOTAL NET ASSETS" 
                        surplus={summaryValues.totalSurplus}
                        adjustments={summaryValues.totalAdjustments}
                        total={netAssets}
                        isHighlighted={true}
                      />
                    )}
                  </DynamicSectionGroup>
                ))}
              </DynamicFinancialTable>
            </div>
          </div>
        </TooltipProvider>
      )}
    </ToastManager>
  );
}
