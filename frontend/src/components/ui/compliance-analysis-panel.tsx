"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, CheckCircle, XCircle, Lightbulb } from "lucide-react";
import type { ComplianceAnalysis } from "@/types";
import { cn, getComplianceColor, getComplianceLabel } from "@/lib/utils";

interface ComplianceAnalysisPanelProps {
  analysis: ComplianceAnalysis;
  platform: string;
}

export function ComplianceAnalysisPanel({
  analysis,
  platform,
}: ComplianceAnalysisPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-bg-card rounded-xl border border-border overflow-hidden">
      {/* Toggle header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 hover:bg-bg-card-hover transition-colors"
      >
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-bold">AI Compliance Analysis</h3>
          <span
            className={cn(
              "text-xs font-semibold px-2 py-0.5 rounded-full",
              analysis.compliance_status === "fully_compliant" &&
                "bg-success/15 text-success",
              analysis.compliance_status === "partially_compliant" &&
                "bg-warning/15 text-warning",
              analysis.compliance_status === "non_compliant" &&
                "bg-danger/15 text-danger"
            )}
          >
            {getComplianceLabel(analysis.compliance_status)}
          </span>
        </div>
        <ChevronDown
          className={cn(
            "w-4 h-4 text-text-secondary transition-transform duration-300",
            isOpen && "rotate-180"
          )}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-4">
              {/* Analysis text */}
              <p className="text-sm text-text-secondary leading-relaxed">
                {analysis.analysis}
              </p>

              {/* Deliverables Met */}
              {analysis.deliverables_met.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                    Deliverables Met
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.deliverables_met.map((item, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm"
                      >
                        <CheckCircle className="w-4 h-4 text-success mt-0.5 shrink-0" />
                        <span className="text-text-secondary">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Deliverables Missing */}
              {analysis.deliverables_missing.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                    Deliverables Missing
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.deliverables_missing.map((item, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm"
                      >
                        <XCircle className="w-4 h-4 text-danger mt-0.5 shrink-0" />
                        <span className="text-text-secondary">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {analysis.recommendations.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">
                    Recommendations
                  </h4>
                  <ul className="space-y-1.5">
                    {analysis.recommendations.map((item, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm"
                      >
                        <Lightbulb className="w-4 h-4 text-neon-blue mt-0.5 shrink-0" />
                        <span className="text-text-secondary">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
