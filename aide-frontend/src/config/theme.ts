import { ThemeConfig } from 'antd';

export const theme: ThemeConfig = {
  token: {
    // Primary colors matching the current AIDE design
    colorPrimary: '#0D0F18',
    colorBgBase: '#F0EFE9',
    colorBgContainer: '#FFFFFF',
    colorBgElevated: '#FFFFFF',
    
    // Text colors
    colorText: '#0D0F18',
    colorTextSecondary: '#666666',
    colorTextTertiary: '#999999',
    
    // Border and divider colors
    colorBorder: '#E5E5E5',
    colorBorderSecondary: '#F0F0F0',
    
    // Success, warning, error colors
    colorSuccess: '#52C41A',
    colorWarning: '#FAAD14',
    colorError: '#FF4D4F',
    colorInfo: '#1890FF',
    
    // Layout
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,
    
    // Typography
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    fontSizeLG: 16,
    fontSizeXL: 20,
    fontSizeHeading1: 38,
    fontSizeHeading2: 30,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,
    
    // Spacing
    padding: 16,
    paddingLG: 24,
    paddingXL: 32,
    paddingSM: 12,
    paddingXS: 8,
    
    // Component specific
    controlHeight: 40,
    controlHeightLG: 48,
    controlHeightSM: 32,
    
    // Box shadow
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
    boxShadowSecondary: '0 4px 16px rgba(0, 0, 0, 0.08)',
  },
  components: {
    Layout: {
      headerBg: '#FFFFFF',
      headerHeight: 64,
      headerPadding: '0 24px',
      siderBg: '#FFFFFF',
      bodyBg: '#F0EFE9',
    },
    Button: {
      borderRadius: 8,
      controlHeight: 40,
      fontWeight: 500,
    },
    Input: {
      borderRadius: 8,
      controlHeight: 40,
    },
    Card: {
      borderRadius: 12,
      paddingLG: 24,
    },
    Tabs: {
      borderRadius: 8,
      cardBg: '#FFFFFF',
    },
    Upload: {
      borderRadius: 8,
    },
    Progress: {
      borderRadius: 8,
    },
    Slider: {
      borderRadius: 8,
    },
    Table: {
      borderRadius: 8,
      headerBg: '#FAFAFA',
    },
    Modal: {
      borderRadius: 12,
    },
    Drawer: {
      borderRadius: 12,
    },
    Message: {
      borderRadius: 8,
    },
    Notification: {
      borderRadius: 8,
    },
  },
};
