export const metadata = {
  title: "Agent Zero Chat",
  description: "CopilotKit frontend connected to Agent Zero via AG-UI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}
