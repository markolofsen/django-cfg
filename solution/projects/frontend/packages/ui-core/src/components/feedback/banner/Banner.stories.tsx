import type { Meta, StoryObj } from '@storybook/react-vite';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';
import {
  Banner,
  Banners,
  BannerActions,
  BannerClose,
  BannerContent,
  BannerDescription,
  BannerIcon,
  BannerTitle,
  Button,
  useBanners,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Feedback/Banner',
  component: Banner,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'Toast-like banner notifications with stacking, priorities, and auto-dismiss.',
      },
    },
  },
} satisfies Meta<typeof Banner>;

export default meta;
type Story = StoryObj<typeof meta>;

function BannerDemo() {
  const { onBannerAdd } = useBanners();
  const variants = [
    { variant: 'info' as const, icon: <Info />, title: 'Info', desc: 'Something happened.' },
    { variant: 'success' as const, icon: <CheckCircle />, title: 'Success', desc: 'Changes saved.' },
    { variant: 'warning' as const, icon: <AlertTriangle />, title: 'Warning', desc: 'Check your input.' },
    { variant: 'destructive' as const, icon: <XCircle />, title: 'Error', desc: 'Request failed.' },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {variants.map((v) => (
        <Button
          key={v.variant}
          variant="outline"
          onClick={() =>
            onBannerAdd({
              variant: v.variant,
              content: (
                <>
                  <BannerIcon>{v.icon}</BannerIcon>
                  <BannerContent>
                    <BannerTitle>{v.title}</BannerTitle>
                    <BannerDescription>{v.desc}</BannerDescription>
                  </BannerContent>
                  <BannerActions>
                    <BannerClose />
                  </BannerActions>
                </>
              ),
              duration: 4000,
            })
          }
        >
          {v.title}
        </Button>
      ))}
    </div>
  );
}

export const Default: Story = {
  render: () => (
    <Banners>
      <BannerDemo />
    </Banners>
  ),
};

export const InlineBanner: Story = {
  render: () => (
    <div className="space-y-4">
      <Banner variant="info">
        <BannerIcon>
          <Info />
        </BannerIcon>
        <BannerContent>
          <BannerTitle>Update Available</BannerTitle>
          <BannerDescription>A new version is ready to install.</BannerDescription>
        </BannerContent>
        <BannerActions>
          <Button size="sm">Update</Button>
          <BannerClose />
        </BannerActions>
      </Banner>
      <Banner variant="success">
        <BannerIcon>
          <CheckCircle />
        </BannerIcon>
        <BannerContent>
          <BannerTitle>Success</BannerTitle>
          <BannerDescription>Your changes have been saved.</BannerDescription>
        </BannerContent>
        <BannerActions>
          <BannerClose />
        </BannerActions>
      </Banner>
      <Banner variant="warning">
        <BannerIcon>
          <AlertTriangle />
        </BannerIcon>
        <BannerContent>
          <BannerTitle>Warning</BannerTitle>
          <BannerDescription>Your subscription expires in 3 days.</BannerDescription>
        </BannerContent>
        <BannerActions>
          <Button size="sm" variant="outline">
            Renew
          </Button>
          <BannerClose />
        </BannerActions>
      </Banner>
      <Banner variant="destructive">
        <BannerIcon>
          <XCircle />
        </BannerIcon>
        <BannerContent>
          <BannerTitle>Error</BannerTitle>
          <BannerDescription>Failed to connect to the server.</BannerDescription>
        </BannerContent>
        <BannerActions>
          <Button size="sm" variant="outline">
            Retry
          </Button>
          <BannerClose />
        </BannerActions>
      </Banner>
    </div>
  ),
};

export const NonDismissible: Story = {
  render: () => (
    <Banner variant="info" dismissible={false}>
      <BannerIcon>
        <Info />
      </BannerIcon>
      <BannerContent>
        <BannerTitle>Important Notice</BannerTitle>
        <BannerDescription>This banner cannot be dismissed by the user.</BannerDescription>
      </BannerContent>
    </Banner>
  ),
};

export const QueueDemo: Story = {
  render: () => {
    function QueueButtons() {
      const { onBannerAdd, onBannersClear } = useBanners();
      return (
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={() =>
              onBannerAdd({
                variant: 'info',
                content: `Notification at ${new Date().toLocaleTimeString()}`,
                duration: 5000,
              })
            }
          >
            Add Banner
          </Button>
          <Button variant="outline" onClick={onBannersClear}>
            Clear All
          </Button>
        </div>
      );
    }
    return (
      <Banners maxVisible={3}>
        <QueueButtons />
      </Banners>
    );
  },
};
