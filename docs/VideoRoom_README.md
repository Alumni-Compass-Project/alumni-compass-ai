# VideoRoom.jsx README

هذا الملف يوضح كيفية استخدام وتضمين مكون `VideoRoom.jsx` في تطبيق React الخاص بك.

## 📦 التثبيت

يتطلب مكون `VideoRoom.jsx` بعض المكتبات الخارجية لإدارة اتصالات WebRTC و WebSocket. قم بتثبيتها باستخدام `npm` أو `yarn`:

```bash
npm install simple-peer socket.io-client prop-types
# أو
yarn add simple-peer socket.io-client prop-types
```

## 🚀 كيفية الاستخدام

`VideoRoom.jsx` هو مكون React واحد يوفر وظائف مؤتمرات الفيديو والصوت ومشاركة الشاشة والمحادثة النصية. لتضمينه في تطبيقك، قم باستيراده واستخدامه كالتالي:

```jsx
import React from 'react';
import VideoRoom from './webrtc-component/VideoRoom'; // تأكد من المسار الصحيح

function App() {
  const handleLeaveCall = () => {
    console.log('المستخدم غادر المكالمة');
    // هنا يمكنك إضافة منطق لإعادة توجيه المستخدم أو تنظيف الحالة
  };

  const handleError = (error) => {
    console.error('حدث خطأ في المكالمة:', error);
    // هنا يمكنك عرض رسالة خطأ للمستخدم
  };

  return (
    <div className="App">
      <h1>مرحباً بك في Alumni Compass Video Call</h1>
      <VideoRoom
        roomId="unique-room-id-123"
        userId="user-123"
        userName="اسم المستخدم"
        userRole="mentor" // أو "graduate"
        onLeave={handleLeaveCall}
        onError={handleError}
      />
    </div>
  );
}

export default App;
```

## ⚙️ Props

المكون يقبل الـ props التالية:

| Prop           | النوع     | مطلوب؟ | الوصف                                                                 |
| :------------- | :------- | :----- | :-------------------------------------------------------------------- |
| `roomId`       | `string`   | نعم    | معرف الغرفة الفريد الذي سينضم إليه المستخدم.                          |
| `userId`       | `string`   | نعم    | المعرف الفريد للمستخدم الحالي.                                        |
| `userName`     | `string`   | نعم    | اسم المستخدم الحالي الذي سيظهر للآخرين.                               |
| `userRole`     | `string`   | نعم    | دور المستخدم، يمكن أن يكون `"mentor"` أو `"graduate"`.              |
| `onLeave`      | `function` | لا      | دالة يتم استدعاؤها عند مغادرة المستخدم للمكالمة.                      |
| `onError`      | `function` | لا      | دالة يتم استدعاؤها عند حدوث خطأ في WebRTC أو الوصول للوسائط.          |

## ⚠️ ملاحظات مهمة

*   **خادم Signaling:** شغّل `signaling-server/` محلياً أو على Railway. في `VideoRoom.jsx` استخدم `REACT_APP_SIGNALING_URL`.
*   **STUN Servers:** Google STUN servers are configured for peer discovery.
*   **Audio-only mode:** زر **صوت فقط** يوقف الفيديو ويبقي الصوت نشطاً.
*   **اللغة العربية (RTL):** تم تصميم واجهة المستخدم لدعم اتجاه النص من اليمين إلى اليسار (RTL) بشكل افتراضي.
*   **النمط:** تم تضمين أنماط CSS الأساسية مباشرة في المكون لأغراض التوضيح. في تطبيق إنتاجي، قد ترغب في استخراج هذه الأنماط إلى ملفات CSS منفصلة أو استخدام مكتبة أنماط.
