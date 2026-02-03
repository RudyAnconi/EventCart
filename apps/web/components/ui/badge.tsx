import * as React from "react";

import { cn } from "@/lib/utils";

const Badge = React.forwardRef<HTMLSpanElement, React.HTMLAttributes<HTMLSpanElement>>(
  ({ className, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center rounded-full bg-slate-800 px-3 py-1 text-xs font-medium text-slate-200",
        className
      )}
      {...props}
    />
  )
);
Badge.displayName = "Badge";

export { Badge };
