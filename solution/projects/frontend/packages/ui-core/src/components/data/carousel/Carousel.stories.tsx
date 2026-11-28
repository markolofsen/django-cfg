import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Card,
  CardContent,
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Carousel',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Carousel className="w-[480px]">
      <CarouselContent>
        {Array.from({ length: 5 }).map((_, i) => (
          <CarouselItem key={i}>
            <Card>
              <CardContent className="flex aspect-[16/9] items-center justify-center text-3xl font-semibold">
                {i + 1}
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  ),
};

export const Wide: Story = {
  render: () => (
    <Carousel className="w-[640px]">
      <CarouselContent>
        {Array.from({ length: 3 }).map((_, i) => (
          <CarouselItem key={i}>
            <Card>
              <CardContent className="flex aspect-video items-center justify-center bg-muted text-3xl font-semibold">
                Slide {i + 1}
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  ),
};

export const WithImages: Story = {
  render: () => (
    <Carousel className="w-[480px]">
      <CarouselContent>
        {[
          'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400',
          'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400',
          'https://images.unsplash.com/photo-1542362567-b07e54358753?w=400',
        ].map((src, i) => (
          <CarouselItem key={i}>
            <div className="aspect-video overflow-hidden rounded-lg">
              <img
                src={src}
                alt={`Slide ${i + 1}`}
                className="h-full w-full object-cover"
              />
            </div>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  ),
};

export const Loop: Story = {
  render: () => (
    <Carousel className="w-[480px]" opts={{ loop: true }}>
      <CarouselContent>
        {Array.from({ length: 5 }).map((_, i) => (
          <CarouselItem key={i}>
            <Card>
              <CardContent className="flex aspect-[16/9] items-center justify-center text-3xl font-semibold">
                {i + 1}
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  ),
};

export const MultiPerView: Story = {
  render: () => (
    <Carousel
      className="w-[640px]"
      opts={{ align: 'start' }}
    >
      <CarouselContent>
        {Array.from({ length: 9 }).map((_, i) => (
          <CarouselItem key={i} className="basis-1/3">
            <Card>
              <CardContent className="flex aspect-square items-center justify-center text-2xl font-semibold">
                {i + 1}
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  ),
};
