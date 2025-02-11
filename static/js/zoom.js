document.addEventListener("DOMContentLoaded", async () => {
    try {
      if (!meetingConfig.userName || meetingConfig.userName === "Guest") {
        console.warn("⚠️ No participant name found. Using 'Guest'.");
      }
      if (!meetingConfig.userEmail || meetingConfig.userEmail === "email@example.com") {
        console.warn("⚠️ No participant email found. Using 'email@example.com'.");
      }
  
      ZoomMtg.init({
        leaveUrl: meetingConfig.leaveUrl,
        isSupportAV: true,
        success: () => {
          console.log("✅ Zoom SDK initialized successfully.");
          ZoomMtg.join({
            meetingNumber: meetingConfig.meetingId,
            userName: meetingConfig.userName,
            signature: meetingConfig.signature,
            sdkKey: meetingConfig.sdkKey,
            userEmail: meetingConfig.userEmail,
            passWord: "Impilo",
            success: (res) => console.log("✅ Joined meeting successfully", res),
            error: (err) => console.error("❌ Join meeting error", err),
          });
        },
        error: (err) => console.error("❌ Init Zoom SDK error", err),
      });
  
    } catch (error) {
      console.error("❌ Error initializing Zoom SDK:", error);
    }
  });
  